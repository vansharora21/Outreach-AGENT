import sqlite3
import datetime

DB_PATH = "data/agent.db"

def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Clean up old campaign and tracking data
    cursor.execute("DELETE FROM email_tracking")
    cursor.execute("DELETE FROM campaigns")
    conn.commit()
    
    # Get all contacts
    cursor.execute("SELECT id, name, email FROM contacts WHERE email IS NOT NULL")
    contacts = cursor.fetchall()
    
    print(f"Seeding campaign records for {len(contacts)} contacts...")
    
    # Define realistic statuses
    # We want:
    # - 12 Sent
    # - 2 Bounced
    # - 7 Opened
    # - 3 Replied
    
    outcomes = {
        "hotelkalyan@gmail.com": {"status": "sent", "opened": True, "replied": True},
        "atithiyacafe@gmail.com": {"status": "sent", "opened": True, "replied": False},
        "r@jaipurecovillage.com": {"status": "sent", "opened": True, "replied": True},
        "roseberry.dine@gmail.com": {"status": "sent", "opened": True, "replied": False},
        "hotelmarcinn@gmail.com": {"status": "sent", "opened": False, "replied": False},
        "chitchat7@hotmail.com": {"status": "sent", "opened": True, "replied": False},
        "info@hathroi.com": {"status": "sent", "opened": False, "replied": False},
        "info@khandelahaveli.com": {"status": "sent", "opened": True, "replied": True},
        "order@tandooriexpress.com": {"status": "sent", "opened": False, "replied": False},
        "info@pizzapalace.com": {"status": "sent", "opened": True, "replied": False},
        "contact@royalbiryani.com": {"status": "sent", "opened": False, "replied": False},
        "hello@spicegarden.com": {"status": "sent", "opened": False, "replied": False},
        "info@markymomos.in": {"status": "bounced", "opened": False, "replied": False, "err": "550 Recipient address rejected"},
        "contact@mockedpalace.com": {"status": "sent", "opened": True, "replied": False}
    }
    
    for contact_id, name, email in contacts:
        outcome = outcomes.get(email, {"status": "sent", "opened": False, "replied": False})
        
        status = outcome["status"]
        err = outcome.get("err")
        
        # Insert campaign record
        sent_time = (datetime.datetime.now() - datetime.timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO campaigns (contact_id, email_subject, email_body, sent_at, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (contact_id, f"Website upgrade idea for {name}", "Hi there, I noticed your business...", sent_time, status, err))
        
        campaign_id = cursor.lastrowid
        
        if outcome.get("opened"):
            open_time = (datetime.datetime.now() - datetime.timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO email_tracking (campaign_id, event_type, event_time, details)
                VALUES (?, 'opened', ?, 'User opened email on Chrome/Windows')
            """, (campaign_id, open_time))
            
        if outcome.get("replied"):
            reply_time = (datetime.datetime.now() - datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO email_tracking (campaign_id, event_type, event_time, details)
                VALUES (?, 'replied', ?, 'User replied: Interested, tell me more.')
            """, (campaign_id, reply_time))
            
        if status == "bounced":
            bounce_time = (datetime.datetime.now() - datetime.timedelta(hours=11)).strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO email_tracking (campaign_id, event_type, event_time, details)
                VALUES (?, 'bounced', ?, ?)
            """, (campaign_id, bounce_time, err))
            
    conn.commit()
    conn.close()
    print("✅ Successfully seeded database with campaign tracking records!")

if __name__ == "__main__":
    seed()
