import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.campaign import CampaignPolicy, enforce_daily_cap, select_leads


def test_select_leads_excludes_low_confidence_and_generated(monkeypatch):
    contacts = [
        {"id": 1, "name": "Verified", "email": "info@verified.test", "email_source": "website", "confidence_score": 0.9},
        {"id": 2, "name": "Guess", "email": "info@guess.test", "email_source": "generated", "confidence_score": 0.9},
        {"id": 3, "name": "Weak", "email": "info@weak.test", "email_source": "osm", "confidence_score": 0.4},
    ]
    monkeypatch.setattr("utils.campaign.get_contacts_for_outreach", lambda **_: contacts)

    approved, excluded = select_leads(CampaignPolicy(max_leads=5, min_confidence=0.7))

    assert [lead["name"] for lead in approved] == ["Verified"]
    assert {lead["name"] for lead in excluded} == {"Guess", "Weak"}


def test_daily_cap_limits_selection(monkeypatch):
    monkeypatch.setattr("utils.campaign.count_sent_today", lambda: 23)
    leads = [{"id": 1}, {"id": 2}, {"id": 3}]
    assert enforce_daily_cap(leads, CampaignPolicy(daily_send_cap=25)) == leads[:2]
