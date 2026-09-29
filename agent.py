"""Review-first outreach sender.

Run ``python scraper.py --type restaurant`` to build the lead pool, then use
this module to preview or intentionally deliver a confidence-gated campaign.
"""

import argparse
import smtplib
import time
from typing import List

from config import EMAIL_ADDRESS, EMAIL_PASSWORD
from utils.ai_email import generate_email
from utils.campaign import CampaignPolicy, enforce_daily_cap, record_delivery, select_leads
from utils.database import init_database
from utils.email_sender import send_email

DEMO_LEADS = [
    {"id": 0, "name": "Northstar Digital", "email": "hello@northstar.example.com", "email_source": "website", "confidence_score": 0.92},
    {"id": 0, "name": "Harbor & Hearth", "email": "contact@harborhearth.example.com", "email_source": "osm", "confidence_score": 0.84},
    {"id": 0, "name": "Cedar Talent Partners", "email": "info@cedartalent.example.com", "email_source": "manual", "confidence_score": 0.96},
]


def subject_for(name: str) -> str:
    return f"A digital idea for {name}"


def preview(leads: List[dict], business_type: str) -> None:
    print("\nCAMPAIGN PREVIEW (nothing has been sent)")
    print("=" * 60)
    for index, lead in enumerate(leads, 1):
        body = generate_email(lead["name"], business_type=business_type)
        print(f"[{index}] {lead['name']} <{lead['email']}> | {lead['confidence_score']:.0%} | {lead['email_source']}")
        print(f"Subject: {subject_for(lead['name'])}")
        print(f"{body}\n")


def run_demo(business_type: str = "service_business") -> int:
    """Render a deterministic, no-network, no-send campaign demonstration."""
    print("SAFE CAMPAIGN SIMULATION")
    print("Synthetic example.com recipients only; no database writes or email delivery.")
    preview(DEMO_LEADS, business_type)
    print(f"Simulation summary: {len(DEMO_LEADS)} reviewed leads | 0 emails sent | 0 database writes")
    return len(DEMO_LEADS)


def run_campaign(test_mode: bool = True, max_leads: int = 10, min_confidence: float = 0.70,
                 daily_cap: int = 25, business_type: str = "restaurant") -> int:
    """Preview leads in test mode or send a bounded, verified campaign."""
    init_database()
    policy = CampaignPolicy(min_confidence=min_confidence, max_leads=max_leads, daily_send_cap=daily_cap)
    approved, excluded = select_leads(policy)
    sendable = enforce_daily_cap(approved, policy)

    print(f"Eligible leads: {len(approved)} | Excluded by policy: {len(excluded)} | Daily-cap available: {len(sendable)}")
    for lead in excluded:
        print(f"  Excluded: {lead['name']} — {lead['exclusion_reason']}")
    if not sendable:
        return 0
    if test_mode:
        preview(sendable, business_type)
        return len(sendable)
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise RuntimeError("EMAIL_ADDRESS and EMAIL_PASSWORD must be configured before live delivery")

    delivered = 0
    for lead in sendable:
        subject = subject_for(lead["name"])
        body = generate_email(lead["name"], business_type=business_type)
        try:
            send_email(EMAIL_ADDRESS, EMAIL_PASSWORD, lead["email"], subject, body)
            record_delivery(lead, subject, body, "sent")
            delivered += 1
            time.sleep(4)
        except smtplib.SMTPRecipientsRefused as exc:
            record_delivery(lead, subject, body, "bounced", str(exc))
        except Exception as exc:
            record_delivery(lead, subject, body, "failed", str(exc))
    return delivered


def main(test_mode: bool = True, **kwargs) -> int:
    return run_campaign(test_mode=test_mode, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Confidence-gated outreach campaign runner")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Preview messages; this is the default")
    mode.add_argument("--send", action="store_true", help="Deliver messages after an explicit confirmation flag")
    mode.add_argument("--demo", action="store_true", help="Run a no-network simulation with synthetic leads")
    parser.add_argument("--confirm-send", action="store_true", help="Required together with --send")
    parser.add_argument("--max-leads", type=int, default=10)
    parser.add_argument("--min-confidence", type=float, default=0.70)
    parser.add_argument("--daily-cap", type=int, default=25)
    parser.add_argument("--type", default="restaurant")
    args = parser.parse_args()
    if args.send and not args.confirm_send:
        parser.error("--send requires --confirm-send")
    if not 0 <= args.min_confidence <= 1 or args.max_leads < 1 or args.daily_cap < 1:
        parser.error("confidence must be 0–1; caps must be positive")
    if args.demo:
        run_demo(args.type)
    else:
        run_campaign(test_mode=not args.send, max_leads=args.max_leads, min_confidence=args.min_confidence,
                     daily_cap=args.daily_cap, business_type=args.type)
