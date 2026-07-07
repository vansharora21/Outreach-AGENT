import os
import sys
import json
import sqlite3
from pathlib import Path

# Add project root to path to import analytics
sys.path.insert(0, str(Path(__file__).parent.parent))

from analytics import (
    get_campaign_performance_by_cuisine,
    get_email_source_breakdown,
    get_sendability_report,
    get_quality_score_distribution,
    get_daily_activity,
    get_top_quality_contacts
)

DB_PATH = "data/agent.db"
OUTPUT_PATH = "results/dashboard_data.js"

def main():
    print("📊 Exporting database analytics to JavaScript for the showcase dashboard...")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}. Run scraping first!")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Overall Funnel Metrics
    cursor.execute("SELECT COUNT(*) FROM contacts")
    total_found = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM contacts WHERE email IS NOT NULL")
    emails_found = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM campaigns")
    total_campaigns = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE event_type = 'opened'")
    total_opened = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM email_tracking WHERE event_type = 'replied'")
    total_replied = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'bounced'")
    total_bounced = cursor.fetchone()[0]
    
    conn.close()
    
    # Calculate rates
    bounce_rate = round(100.0 * total_bounced / max(total_campaigns, 1), 1)
    # Open rate is calculated against delivered emails (sent minus bounced)
    delivered = total_campaigns - total_bounced
    open_rate = round(100.0 * total_opened / max(delivered, 1), 1)
    
    # Generate JSON data structure
    dashboard_data = {
        "summary": {
            "total_found": total_found,
            "emails_found": emails_found,
            "emails_sent": total_campaigns,
            "emails_opened": total_opened,
            "emails_replied": total_replied,
            "emails_bounced": total_bounced,
            "bounce_rate": bounce_rate,
            "open_rate": open_rate,
            "email_finding_rate": round(100.0 * emails_found / max(total_found, 1), 1)
        },
        "cuisine_performance": get_campaign_performance_by_cuisine(),
        "email_source_breakdown": get_email_source_breakdown(),
        "sendability_report": get_sendability_report(),
        "quality_distribution": get_quality_score_distribution(),
        "daily_activity": get_daily_activity(),
        "top_contacts": get_top_quality_contacts(10)
    }
    
    # Ensure results folder exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("window.dashboardData = ")
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
        f.write(";\n")
        
    print(f"✅ Successfully exported analytics to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
