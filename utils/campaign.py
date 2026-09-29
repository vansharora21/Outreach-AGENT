"""Campaign orchestration with review-first and deliverability safeguards."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

from utils.database import count_sent_today, get_contacts_for_outreach, log_campaign

VERIFIED_SOURCES = {"website", "osm", "hunter", "clearbit", "manual"}


@dataclass(frozen=True)
class CampaignPolicy:
    min_confidence: float = 0.70
    daily_send_cap: int = 25
    max_leads: int = 10
    allow_generated_addresses: bool = False


def select_leads(policy: CampaignPolicy) -> Tuple[List[Dict], List[Dict]]:
    """Return sendable leads and excluded leads with an explicit reason."""
    candidates = get_contacts_for_outreach(limit=policy.max_leads * 5, exclude_contacted=True)
    approved, excluded = [], []
    for contact in candidates:
        source = (contact.get("email_source") or "").lower()
        confidence = float(contact.get("confidence_score") or 0)
        reason = None
        if confidence < policy.min_confidence:
            reason = f"confidence {confidence:.0%} is below {policy.min_confidence:.0%}"
        elif source == "generated" and not policy.allow_generated_addresses:
            reason = "pattern-generated address requires manual verification"
        elif source not in VERIFIED_SOURCES and not (source == "generated" and policy.allow_generated_addresses):
            reason = f"unapproved email source: {source or 'unknown'}"
        if reason:
            excluded.append({**contact, "exclusion_reason": reason})
        elif len(approved) < policy.max_leads:
            approved.append(contact)
    return approved, excluded


def enforce_daily_cap(leads: List[Dict], policy: CampaignPolicy) -> List[Dict]:
    return leads[:max(policy.daily_send_cap - count_sent_today(), 0)]


def record_delivery(contact: Dict, subject: str, body: str, status: str, error: str = None) -> int:
    """Persist a single, auditable delivery result."""
    return log_campaign(contact["id"], subject, body, status=status, error_message=error)
