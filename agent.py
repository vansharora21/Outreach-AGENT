from utils.search import get_restaurants
from utils.filter import filter_no_website, calculate_contact_quality_score, rank_restaurants
from utils.email_sender import send_email
from utils.database import init_database, add_contact, log_campaign, get_campaign_stats, is_on_do_not_contact_list
from utils.ai_email import generate_email
from utils.email_finder import find_email_multi_strategy

from search_config import get_config
from config import (
    EMAIL_ADDRESS,
    EMAIL_PASSWORD,
    LOCATION_COORDS
)

import time
import sys


def find_best_email(restaurant: dict, business_type: str = "restaurant") -> tuple:
    """
    Try to find email for business using multiple strategies.
    Returns (email, source, confidence_score)
    
    Strategies (priority order):
    1. Existing email in database
    2. Website scraping (70-90% confidence)
    3. Clearbit API lookup (95% confidence)
    4. Hunter.io API lookup (80-95% confidence)
    5. Email pattern generation (50-60% confidence)
    """
    name = restaurant.get("name")
    website = restaurant.get("website")
    domain = website.replace("http://", "").replace("https://", "").split("/")[0] if website else None
    
    # Strategy 0: Already has email in OSM data
    if restaurant.get("email"):
        return (restaurant["email"], "osm", 0.8)
    
    # Multi-strategy email finding
    result = find_email_multi_strategy(
        business_name=name,
        website=website,
        domain=domain,
        business_type=business_type
    )
    
    if result:
        source, email, confidence = result
        return (email, source, confidence)
    
    return (None, None, 0.0)


def main(test_mode=False, auto_export=True, business_type: str = "restaurant"):
    print("🚀 Agent started...\n")
    print(f"📌 Searching for: {business_type.replace('_', ' ').title()}\n")
    
    # Initialize SQLite database
    print("📊 Initializing database...")
    init_database()
    
    if test_mode:
        print("🧪 TEST MODE - Emails will NOT be sent\n")

    # 2️⃣ Search for nearby businesses using Overpass API (FREE - no API key needed!)
    print("🔍 Searching for businesses using OpenStreetMap...")
    businesses = get_restaurants(
        location=LOCATION_COORDS,
        radius=5000  # 5km radius
    )

    if not businesses:
        print("❌ No businesses found. Check your location coordinates.")
        return

    print(f"✅ Found {len(businesses)} businesses\n")

    # 3️⃣ Filter businesses WITHOUT websites
    print("🧹 Filtering businesses without websites...")
    filtered_businesses = filter_no_website(businesses)

    print(f"✅ {len(filtered_businesses)} businesses have NO website\n")

    # 4️⃣ Rank businesses by quality
    print("📊 Ranking businesses by quality...")
    ranked_businesses = rank_restaurants(filtered_businesses)
    
    # 5️⃣ Find emails and prepare for outreach
    print("📧 Finding contact emails for businesses (90% target success rate)...\n")
    
    ready_for_outreach = []
    email_found_count = 0
    email_not_found_count = 0
    
    for business in ranked_businesses:
        name = business.get("name")
        email, email_source, confidence = find_best_email(business, business_type)
        
        # Skip if already in do-not-contact list
        if email and is_on_do_not_contact_list(email=email):
            print(f"⏭️ Skipping {name} (on do-not-contact list)")
            continue
        
        if not email:
            email_not_found_count += 1
            print(f"⚠️ No email found for {name} - skipping...")
            continue
        
        email_found_count += 1
        
        # Calculate quality score
        quality_score = calculate_contact_quality_score(business)
        
        # Add to database
        contact_id = add_contact(
            name=name,
            email=email,
            phone=business.get("phone"),
            website=business.get("website"),
            cuisine=business.get("cuisine"),
            opening_hours=business.get("opening_hours"),
            osm_id=str(business.get("osm_id")),
            latitude=business.get("lat"),
            longitude=business.get("lon"),
            email_source=email_source,
            confidence_score=confidence
        )
        
        print(f"✅ {name}")
        print(f"   Email: {email}")
        print(f"   Source: {email_source} | Confidence: {confidence*100:.0f}%")
        print(f"   Quality: {quality_score*100:.0f}%\n")
        
        ready_for_outreach.append({
            "contact_id": contact_id,
            "business": business,
            "email": email,
            "email_source": email_source,
            "confidence": confidence,
            "quality_score": quality_score
        })
    
    # Show email finding rate
    total_searched = len(ranked_businesses)
    if total_searched > 0:
        email_rate = (email_found_count / total_searched) * 100
        print(f"\n📊 EMAIL FINDING RATE: {email_rate:.1f}% ({email_found_count}/{total_searched})")
        print(f"   Target: 90% | Current: {email_rate:.1f}%\n")
    
    print(f"📈 Ready for outreach: {len(ready_for_outreach)} businesses\n")
    
    # 6️⃣ Loop through businesses and send emails
    for idx, item in enumerate(ready_for_outreach, 1):
        contact_id = item["contact_id"]
        business = item["business"]
        email = item["email"]
        name = business.get("name")
        
        print(f"[{idx}/{len(ready_for_outreach)}] ✉️ Preparing email for {name}")

        # Generate AI email
        email_body = generate_email(name)
        email_subject = f"Website idea for {name}"

        # Send email (or test mode)
        if test_mode:
            print(f"📧 [TEST MODE] Would send email to {name}")
            print(f"   To: {email}")
            print(f"   Subject: {email_subject}")
            print(f"   Body: {email_body[:100]}...\n")
            log_campaign(contact_id, email_subject, email_body, status="test_mode")
            
        else:
            try:
                send_email(
                    sender=EMAIL_ADDRESS,
                    password=EMAIL_PASSWORD,
                    to=email,
                    subject=email_subject,
                    body=email_body
                )

                print(f"✅ Email sent to {name}")
                log_campaign(contact_id, email_subject, email_body, status="sent")

                # Rate limit (VERY IMPORTANT)
                time.sleep(4)

            except Exception as e:
                print(f"❌ Failed to send email to {name}: {e}")
                log_campaign(contact_id, email_subject, email_body, status="failed", 
                           error_message=str(e))

    # 7️⃣ Print campaign statistics
    print("\n" + "="*50)
    print("📊 CAMPAIGN STATISTICS")
    print("="*50)
    stats = get_campaign_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    # 8️⃣ Export data to CSV
    if auto_export and not test_mode:
        from utils.export import export_all_data, export_summary_report
        print("\n📊 Exporting data to CSV...")
        try:
            export_all_data()
            export_summary_report()
            print("✅ Data exported to results/ folder")
        except Exception as e:
            print(f"⚠️ Export failed: {e}")
    
    print("\n🎯 Agent finished successfully.")


if __name__ == "__main__":
    # Check command line arguments
    test_mode = "--test" in sys.argv
    auto_export = "--no-export" not in sys.argv
    
    # Determine business type
    business_type = "restaurant"  # Default
    for arg in sys.argv:
        if arg.startswith("--type="):
            business_type = arg.replace("--type=", "")
            break
    
    main(test_mode=test_mode, auto_export=auto_export, business_type=business_type)
