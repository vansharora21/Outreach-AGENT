"""
Follow-up campaign scheduler.
Manages sending follow-up emails at strategic intervals.
"""

from utils.database import get_contacts_needing_followup, log_campaign
from utils.email_sender import send_email
from utils.ai_email import generate_email
from config import EMAIL_ADDRESS, EMAIL_PASSWORD
import time


FOLLOWUP_TEMPLATES = {
    1: {
        "days": 3,
        "subject_prefix": "Quick follow-up: ",
        "intro": "I hope this email finds you well!\n\nI sent you an email a few days ago about creating a website for {restaurant_name}.\n\nI wanted to reach out one more time to see if this might be of interest to you.\n\n"
    },
    2: {
        "days": 7,
        "subject_prefix": "Last chance: ",
        "intro": "Hi {restaurant_name},\n\nThis is my final outreach regarding website development for your restaurant.\n\nIf you're interested in discussing how a website could benefit your business, I'm here to help.\n\n"
    }
}


def schedule_followups(test_mode=False):
    """
    Check for contacts that need follow-up emails and send them.
    """
    print("🔄 Checking for follow-ups needed...\n")
    
    for round_num, followup_config in FOLLOWUP_TEMPLATES.items():
        days = followup_config["days"]
        
        # Get contacts that need follow-up
        contacts = get_contacts_needing_followup(days_since_first_email=days)
        
        if not contacts:
            print(f"✅ No contacts need {round_num}. follow-up")
            continue
        
        print(f"\n📧 Sending round {round_num} follow-ups ({len(contacts)} contacts)...")
        
        for contact in contacts:
            contact_id = contact["id"]
            name = contact["name"]
            email = contact["email"]
            
            try:
                # Generate personalized follow-up email
                email_body = generate_email(
                    name,
                    followup_template=followup_config.get("intro", "")
                )
                
                subject = followup_config["subject_prefix"] + f"Website for {name}"
                
                if test_mode:
                    print(f"📧 [TEST MODE] Would send follow-up to {name}")
                else:
                    send_email(
                        sender=EMAIL_ADDRESS,
                        password=EMAIL_PASSWORD,
                        to=email,
                        subject=subject,
                        body=email_body
                    )
                    
                    print(f"✅ Follow-up sent to {name}")
                
                # Log campaign
                log_campaign(
                    contact_id,
                    subject,
                    email_body,
                    status="sent",
                    campaign_round=round_num + 1
                )
                
                # Rate limit
                time.sleep(4)
            
            except Exception as e:
                print(f"❌ Failed to send follow-up to {name}: {e}")
                log_campaign(
                    contact_id,
                    subject,
                    email_body,
                    status="failed",
                    error_message=str(e),
                    campaign_round=round_num + 1
                )
    
    print("\n✅ Follow-up scheduler completed.")


if __name__ == "__main__":
    import sys
    test_mode = "--test" in sys.argv
    schedule_followups(test_mode=test_mode)
