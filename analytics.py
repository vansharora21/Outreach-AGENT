"""
Analytics and reporting module.
Provides insights into campaign performance.
"""

from utils.database import init_database
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta


DB_PATH = "data/agent.db"


def get_campaign_performance_by_cuisine() -> dict:
    """Analyze campaign performance grouped by cuisine type."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            c.cuisine,
            COUNT(DISTINCT c.id) as total_contacts,
            COUNT(DISTINCT CASE WHEN cam.status = 'sent' THEN cam.id END) as emails_sent,
            COUNT(DISTINCT CASE WHEN et.event_type = 'replied' THEN et.id END) as replies,
            ROUND(AVG(c.contact_quality_score) * 100, 1) as avg_quality_score
        FROM contacts c
        LEFT JOIN campaigns cam ON c.id = cam.contact_id
        LEFT JOIN email_tracking et ON cam.id = et.campaign_id
        GROUP BY c.cuisine
        ORDER BY emails_sent DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "data": results,
        "headers": ["Cuisine", "Total Contacts", "Emails Sent", "Replies", "Avg Quality Score"]
    }


def get_email_source_breakdown() -> dict:
    """Analyze which email sources are most effective."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            c.email_source,
            COUNT(DISTINCT c.id) as total_contacts,
            COUNT(DISTINCT CASE WHEN cam.status = 'sent' THEN cam.id END) as emails_sent,
            COUNT(DISTINCT CASE WHEN et.event_type = 'replied' THEN et.id END) as replies,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN et.event_type = 'replied' THEN et.id END) / 
                NULLIF(COUNT(DISTINCT CASE WHEN cam.status = 'sent' THEN cam.id END), 0), 1) as reply_rate
        FROM contacts c
        LEFT JOIN campaigns cam ON c.id = cam.contact_id
        LEFT JOIN email_tracking et ON cam.id = et.campaign_id
        GROUP BY c.email_source
        ORDER BY reply_rate DESC NULLS LAST
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "data": results,
        "headers": ["Email Source", "Total Contacts", "Emails Sent", "Replies", "Reply Rate %"]
    }


def get_sendability_report() -> dict:
    """Report on emails that couldn't be sent and why."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            error_message,
            COUNT(*) as count
        FROM campaigns
        WHERE status = 'failed'
        GROUP BY error_message
        ORDER BY count DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "data": results,
        "headers": ["Error", "Count"]
    }


def get_quality_score_distribution() -> dict:
    """Show distribution of contact quality scores."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            CASE 
                WHEN contact_quality_score >= 0.8 THEN 'Excellent (0.8-1.0)'
                WHEN contact_quality_score >= 0.6 THEN 'Good (0.6-0.8)'
                WHEN contact_quality_score >= 0.4 THEN 'Fair (0.4-0.6)'
                ELSE 'Poor (<0.4)'
            END as quality_bracket,
            COUNT(*) as count,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM contacts), 1) as percentage
        FROM contacts
        GROUP BY quality_bracket
        ORDER BY contact_quality_score DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "data": results,
        "headers": ["Quality Bracket", "Count", "Percentage %"]
    }


def get_daily_activity() -> dict:
    """Show activity summary by day."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            DATE(sent_at) as date,
            COUNT(*) as emails_sent,
            SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as successful,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
        FROM campaigns
        WHERE sent_at IS NOT NULL
        GROUP BY DATE(sent_at)
        ORDER BY date DESC
        LIMIT 30
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    return {
        "data": results,
        "headers": ["Date", "Total", "Successful", "Failed"]
    }


def get_top_quality_contacts(limit: int = 10) -> dict:
    """Get top quality contacts (best targets for outreach)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT 
            name,
            email,
            cuisine,
            contact_quality_score,
            email_source,
            CASE WHEN id IN (SELECT DISTINCT contact_id FROM campaigns) 
                 THEN 'Yes' ELSE 'No' END as already_contacted
        FROM contacts
        ORDER BY contact_quality_score DESC
        LIMIT ?
    """
    
    cursor.execute(query, (limit,))
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def print_performance_report():
    """Print comprehensive performance report."""
    init_database()
    
    print("\n" + "="*70)
    print("📊 RESTAURANT OUTREACH AGENT - ANALYTICS REPORT")
    print("="*70)
    
    # Performance by cuisine
    print("\n🍽️ PERFORMANCE BY CUISINE")
    print("-" * 70)
    cuisine_data = get_campaign_performance_by_cuisine()
    for row in cuisine_data["data"]:
        print(f"{row[0] or 'Unknown':<20} | Contacts: {row[1]:<4} | Sent: {row[2]:<3} | "
              f"Replies: {row[3]:<3} | Avg Quality: {row[4]}%")
    
    # Email source breakdown
    print("\n📧 EMAIL SOURCE EFFECTIVENESS")
    print("-" * 70)
    source_data = get_email_source_breakdown()
    for row in source_data["data"]:
        print(f"{row[0] or 'Unknown':<15} | Contacts: {row[1]:<4} | Sent: {row[2]:<3} | "
              f"Replies: {row[3]:<3} | Reply Rate: {row[4]}%")
    
    # Quality score distribution
    print("\n📈 CONTACT QUALITY DISTRIBUTION")
    print("-" * 70)
    quality_data = get_quality_score_distribution()
    for row in quality_data["data"]:
        print(f"{row[0]:<20} | Count: {row[1]:<4} | Percentage: {row[2]}%")
    
    # Failed emails
    print("\n❌ SENDABILITY ISSUES")
    print("-" * 70)
    failed_data = get_sendability_report()
    if failed_data["data"]:
        for row in failed_data["data"]:
            print(f"  • {row[0]}: {row[1]} times")
    else:
        print("  ✅ No failed emails!")
    
    # Top contacts
    print("\n⭐ TOP 10 QUALITY CONTACTS")
    print("-" * 70)
    top_contacts = get_top_quality_contacts(10)
    for i, contact in enumerate(top_contacts, 1):
        status = "✅" if contact["already_contacted"] == "Yes" else "⏭️"
        print(f"{i}. {contact['name']:<25} | {contact['email']:<30} | "
              f"Quality: {contact['contact_quality_score']*100:.0f}% {status}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print_performance_report()
