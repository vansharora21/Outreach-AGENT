"""
Export data from SQLite database to CSV files.
Generates reports and exports contacts to results folder.
"""

import sqlite3
import csv
import os
from datetime import datetime
from typing import List

DB_PATH = "data/agent.db"
RESULTS_DIR = "results"


def ensure_results_dir():
    """Create results directory if it doesn't exist."""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def export_contacts_to_csv(filename: str = None) -> str:
    """
    Export all contacts from database to CSV file.
    
    Args:
        filename: Optional custom filename (default: contacts_TIMESTAMP.csv)
    
    Returns:
        Path to exported file
    """
    ensure_results_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"contacts_{timestamp}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query all contacts
    cursor.execute("""
        SELECT 
            id,
            name,
            email,
            phone,
            website,
            cuisine,
            opening_hours,
            email_source,
            ROUND(confidence_score * 100, 1) as confidence_score_pct,
            ROUND(contact_quality_score * 100, 1) as quality_score_pct,
            created_at
        FROM contacts
        ORDER BY contact_quality_score DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Name', 'Email', 'Phone', 'Website', 
            'Cuisine', 'Opening Hours', 'Email Source',
            'Email Confidence %', 'Quality Score %', 'Added Date'
        ])
        writer.writerows(rows)
    
    return filepath


def export_campaigns_to_csv(filename: str = None) -> str:
    """
    Export all email campaigns to CSV file.
    
    Args:
        filename: Optional custom filename
    
    Returns:
        Path to exported file
    """
    ensure_results_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"campaigns_{timestamp}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query all campaigns with contact info
    cursor.execute("""
        SELECT 
            cam.id,
            c.name,
            c.email,
            cam.email_subject,
            cam.status,
            cam.campaign_round,
            cam.sent_at,
            cam.error_message
        FROM campaigns cam
        JOIN contacts c ON cam.contact_id = c.id
        ORDER BY cam.sent_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Campaign ID', 'Restaurant Name', 'Email', 'Subject',
            'Status', 'Round', 'Sent Date', 'Error Message'
        ])
        writer.writerows(rows)
    
    return filepath


def export_engagement_to_csv(filename: str = None) -> str:
    """
    Export email engagement data (opens, clicks, replies) to CSV.
    
    Args:
        filename: Optional custom filename
    
    Returns:
        Path to exported file
    """
    ensure_results_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"engagement_{timestamp}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query engagement tracking
    cursor.execute("""
        SELECT 
            et.id,
            c.name,
            c.email,
            et.event_type,
            et.event_time,
            et.details,
            cam.campaign_round
        FROM email_tracking et
        JOIN campaigns cam ON et.campaign_id = cam.id
        JOIN contacts c ON cam.contact_id = c.id
        ORDER BY et.event_time DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Tracking ID', 'Restaurant Name', 'Email', 'Event Type',
            'Event Time', 'Details', 'Campaign Round'
        ])
        writer.writerows(rows)
    
    return filepath


def export_do_not_contact_to_csv(filename: str = None) -> str:
    """
    Export do-not-contact list to CSV.
    
    Args:
        filename: Optional custom filename
    
    Returns:
        Path to exported file
    """
    ensure_results_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"do_not_contact_{timestamp}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query do-not-contact list
    cursor.execute("""
        SELECT 
            id,
            email,
            phone,
            reason,
            created_at
        FROM do_not_contact
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Write to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Email', 'Phone', 'Reason', 'Added Date'])
        writer.writerows(rows)
    
    return filepath


def export_all_data(include_contacts=True, include_campaigns=True, 
                    include_engagement=True, include_dnc=True) -> dict:
    """
    Export all data to CSV files.
    
    Args:
        include_contacts: Export contacts table
        include_campaigns: Export campaigns table
        include_engagement: Export engagement data
        include_dnc: Export do-not-contact list
    
    Returns:
        Dict with paths to all exported files
    """
    exported_files = {}
    
    if include_contacts:
        try:
            path = export_contacts_to_csv()
            exported_files['contacts'] = path
            print(f"✅ Exported contacts to {path}")
        except Exception as e:
            print(f"❌ Failed to export contacts: {e}")
    
    if include_campaigns:
        try:
            path = export_campaigns_to_csv()
            exported_files['campaigns'] = path
            print(f"✅ Exported campaigns to {path}")
        except Exception as e:
            print(f"❌ Failed to export campaigns: {e}")
    
    if include_engagement:
        try:
            path = export_engagement_to_csv()
            exported_files['engagement'] = path
            print(f"✅ Exported engagement data to {path}")
        except Exception as e:
            print(f"❌ Failed to export engagement: {e}")
    
    if include_dnc:
        try:
            path = export_do_not_contact_to_csv()
            exported_files['do_not_contact'] = path
            print(f"✅ Exported do-not-contact list to {path}")
        except Exception as e:
            print(f"❌ Failed to export do-not-contact: {e}")
    
    return exported_files


def export_summary_report(filename: str = None) -> str:
    """
    Export a comprehensive summary report to CSV.
    
    Args:
        filename: Optional custom filename
    
    Returns:
        Path to exported file
    """
    ensure_results_dir()
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_report_{timestamp}.csv"
    
    filepath = os.path.join(RESULTS_DIR, filename)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Summary metrics
    summary_data = []
    
    # Total contacts
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total_contacts = cursor.fetchone()[0]
    summary_data.append(["Total Contacts Identified", total_contacts])
    
    # Emails sent
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'sent'")
    emails_sent = cursor.fetchone()[0]
    summary_data.append(["Total Emails Sent", emails_sent])
    
    # Failed emails
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'failed'")
    emails_failed = cursor.fetchone()[0]
    summary_data.append(["Failed Emails", emails_failed])
    
    # Replies
    cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE event_type = 'replied'")
    replies = cursor.fetchone()[0]
    summary_data.append(["Total Replies Received", replies])
    
    # Opens
    cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE event_type = 'opened'")
    opens = cursor.fetchone()[0]
    summary_data.append(["Total Email Opens", opens])
    
    # Bounce rate
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'bounced'")
    bounces = cursor.fetchone()[0]
    summary_data.append(["Bounced Emails", bounces])
    
    # By cuisine
    cursor.execute("""
        SELECT cuisine, COUNT(*) FROM contacts 
        GROUP BY cuisine ORDER BY COUNT(*) DESC LIMIT 5
    """)
    cuisines = cursor.fetchall()
    summary_data.append(["", ""])
    summary_data.append(["TOP 5 CUISINES", ""])
    for cuisine, count in cuisines:
        summary_data.append([cuisine or "Unknown", count])
    
    # By email source
    cursor.execute("""
        SELECT email_source, COUNT(*) FROM contacts 
        GROUP BY email_source ORDER BY COUNT(*) DESC
    """)
    sources = cursor.fetchall()
    summary_data.append(["", ""])
    summary_data.append(["EMAIL SOURCES", ""])
    for source, count in sources:
        summary_data.append([source or "Unknown", count])
    
    conn.close()
    
    # Write summary to CSV
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerows(summary_data)
    
    return filepath


if __name__ == "__main__":
    print("\n📊 Exporting all data to CSV...\n")
    
    # Export everything
    files = export_all_data()
    
    # Export summary
    summary_file = export_summary_report()
    print(f"✅ Exported summary report to {summary_file}")
    
    print(f"\n✅ All data exported to {RESULTS_DIR}/ folder")
    print(f"\n📁 Files created:")
    for key, path in files.items():
        print(f"   • {path}")
    print(f"   • {summary_file}")
