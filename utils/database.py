import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = "data/agent.db"


def init_database():
    """Initialize SQLite database with proper schema."""
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Contacts table - store unique restaurants
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            osm_id TEXT UNIQUE,
            name TEXT NOT NULL,
            latitude REAL,
            longitude REAL,
            phone TEXT,
            website TEXT,
            cuisine TEXT,
            opening_hours TEXT,
            email TEXT,
            email_source TEXT,  -- 'osm', 'website', 'generated', 'manual'
            confidence_score REAL DEFAULT 0.5,  -- 0-1, higher = more confident email is correct
            contact_quality_score REAL DEFAULT 0.5,  -- Overall quality for outreach
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Email campaigns - track all outreach attempts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            email_subject TEXT,
            email_body TEXT,
            sent_at TIMESTAMP,
            status TEXT,  -- 'pending', 'sent', 'failed', 'bounced'
            error_message TEXT,
            campaign_round INTEGER DEFAULT 1,  -- For follow-ups
            FOREIGN KEY (contact_id) REFERENCES contacts (id)
        )
    """)
    
    # Email tracking - log responses/engagement
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id INTEGER NOT NULL,
            event_type TEXT,  -- 'opened', 'clicked', 'replied', 'bounced'
            event_time TIMESTAMP,
            details TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns (id)
        )
    """)
    
    # Do not contact list
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS do_not_contact (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            phone TEXT,
            reason TEXT,  -- 'unsubscribed', 'no_response_3x', 'not_interested', 'invalid_email'
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def add_contact(name: str, email: str, phone: str = None, website: str = None,
                cuisine: str = None, opening_hours: str = None, osm_id: str = None,
                latitude: float = None, longitude: float = None,
                email_source: str = "manual", confidence_score: float = 0.5) -> int:
    """Add or update a contact in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO contacts 
            (osm_id, name, email, phone, website, cuisine, opening_hours, 
             latitude, longitude, email_source, confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (osm_id, name, email, phone, website, cuisine, opening_hours,
              latitude, longitude, email_source, confidence_score))
        
        conn.commit()
        contact_id = cursor.lastrowid
        return contact_id
    
    except sqlite3.IntegrityError:
        # Contact already exists, update it
        cursor.execute("""
            UPDATE contacts 
            SET email = ?, email_source = ?, confidence_score = ?, updated_at = CURRENT_TIMESTAMP
            WHERE osm_id = ?
        """, (email, email_source, confidence_score, osm_id))
        
        conn.commit()
        cursor.execute("SELECT id FROM contacts WHERE osm_id = ?", (osm_id,))
        contact_id = cursor.fetchone()[0]
        return contact_id
    
    finally:
        conn.close()


def log_campaign(contact_id: int, email_subject: str, email_body: str,
                 status: str = "sent", error_message: str = None,
                 campaign_round: int = 1) -> int:
    """Log an email campaign for a contact."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO campaigns 
        (contact_id, email_subject, email_body, status, error_message, campaign_round, sent_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (contact_id, email_subject, email_body, status, error_message, campaign_round))
    
    conn.commit()
    campaign_id = cursor.lastrowid
    conn.close()
    
    return campaign_id


def get_contact_by_email(email: str) -> Optional[Dict]:
    """Retrieve a contact by email address."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM contacts WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()
    
    return dict(result) if result else None


def is_on_do_not_contact_list(email: str = None, phone: str = None) -> bool:
    """Check if contact is on do-not-contact list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if email:
        cursor.execute("SELECT id FROM do_not_contact WHERE email = ?", (email,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return True
    
    if phone:
        cursor.execute("SELECT id FROM do_not_contact WHERE phone = ?", (phone,))
        result = cursor.fetchone()
        if result:
            conn.close()
            return True
    
    conn.close()
    return False


def add_to_do_not_contact(email: str = None, phone: str = None, reason: str = "manual"):
    """Add contact to do-not-contact list."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR IGNORE INTO do_not_contact (email, phone, reason)
        VALUES (?, ?, ?)
    """, (email, phone, reason))
    
    conn.commit()
    conn.close()


def get_contacts_for_outreach(limit: int = 50, exclude_contacted: bool = True) -> List[Dict]:
    """Get list of contacts ready for outreach."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM contacts WHERE email IS NOT NULL AND email NOT IN (SELECT email FROM do_not_contact WHERE email IS NOT NULL)"
    
    if exclude_contacted:
        query += " AND id NOT IN (SELECT DISTINCT contact_id FROM campaigns)"
    
    query += " ORDER BY contact_quality_score DESC LIMIT ?"
    
    cursor.execute(query, (limit,))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_contacts_needing_followup(days_since_first_email: int = 3) -> List[Dict]:
    """Get contacts that need follow-up emails."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT DISTINCT c.* FROM contacts c
        JOIN campaigns cam ON c.id = cam.contact_id
        WHERE datetime(cam.sent_at) <= datetime('now', '-' || ? || ' days')
        AND cam.campaign_round = 1
        AND c.id NOT IN (
            SELECT DISTINCT contact_id FROM campaigns WHERE campaign_round > 1
        )
        ORDER BY cam.sent_at ASC
    """
    
    cursor.execute(query, (days_since_first_email,))
    results = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in results]


def get_campaign_stats() -> Dict:
    """Get campaign statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'sent'")
    total_sent = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE event_type = 'replied'")
    total_replied = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total_contacts = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "total_contacts": total_contacts,
        "total_emails_sent": total_sent,
        "total_replies": total_replied,
        "reply_rate": round((total_replied / total_sent * 100) if total_sent > 0 else 0, 2)
    }


def close_database():
    """Close database connection (optional cleanup)."""
    pass
