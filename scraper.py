"""
Web Scraper: Step 1 of the outreach workflow
Finds businesses and extracts contact emails.
Results are saved to database for review/export before email automation.
"""

import sys
import argparse
from utils.search import get_restaurants
from utils.filter import filter_no_website, calculate_contact_quality_score, rank_restaurants
from utils.database import init_database, add_contact, is_on_do_not_contact_list
from utils.email_finder import find_email_multi_strategy
from search_config import get_config

from config import LOCATION_COORDS


def scrape_businesses(business_type: str = "restaurant", verbose: bool = True):
    """
    Step 1: Scrape businesses and find emails.
    
    Returns:
        tuple: (total_found, emails_found, ready_for_outreach)
    """
    
    if verbose:
        print("\n" + "="*60)
        print(f"🔍 WEB SCRAPER - Searching for {business_type.replace('_', ' ').title()}")
        print("="*60 + "\n")
    
    # Initialize database
    init_database()
    
    # Step 1: Search for businesses
    if verbose:
        print("📍 Step 1: Searching for businesses using OpenStreetMap...")
    
    businesses = get_restaurants(
        location=LOCATION_COORDS,
        radius=3000  # 3km radius
    )
    
    if not businesses:
        print("❌ No businesses found. Check your location coordinates.")
        return (0, 0, [])
    
    if verbose:
        print(f"✅ Found {len(businesses)} businesses\n")
    
    # Step 2: Filter businesses without websites
    if verbose:
        print("🧹 Step 2: Filtering businesses without websites...")
    
    filtered_businesses = filter_no_website(businesses)
    
    if verbose:
        print(f"✅ {len(filtered_businesses)} businesses have NO website\n")
    
    # Step 3: Rank by quality
    if verbose:
        print("📊 Step 3: Ranking businesses by quality...")
    
    ranked_businesses = rank_restaurants(filtered_businesses)
    
    # Step 4: Find emails
    if verbose:
        print("📧 Step 4: Finding contact emails (multi-strategy approach)...\n")
    
    ready_for_outreach = []
    email_found_count = 0
    email_not_found_count = 0
    
    for idx, business in enumerate(ranked_businesses, 1):
        name = business.get("name")
        website = business.get("website")
        domain = website.replace("http://", "").replace("https://", "").split("/")[0] if website else None
        
        # Try to find email
        result = find_email_multi_strategy(
            business_name=name,
            website=website,
            domain=domain,
            business_type=business_type
        )
        
        email = None
        email_source = None
        confidence = 0.0
        
        if result:
            email_source, email, confidence = result
        else:
            # Check OSM data as fallback
            if business.get("email"):
                email = business["email"]
                email_source = "osm"
                confidence = 0.8
        
        # Skip if on do-not-contact list
        if email and is_on_do_not_contact_list(email=email):
            continue
        
        if not email:
            email_not_found_count += 1
            if verbose and idx % 10 == 0:
                print(f"   ⏳ Processed {idx}/{len(ranked_businesses)} - {email_found_count} emails found")
            continue
        
        email_found_count += 1
        
        # Calculate quality score
        quality_score = calculate_contact_quality_score(business)
        
        # Add to database
        contact_id = add_contact(
            name=name,
            email=email,
            phone=business.get("phone"),
            website=website,
            cuisine=business.get("cuisine"),
            opening_hours=business.get("opening_hours"),
            osm_id=str(business.get("osm_id")),
            latitude=business.get("lat"),
            longitude=business.get("lon"),
            email_source=email_source,
            confidence_score=confidence
        )
        
        ready_for_outreach.append({
            "contact_id": contact_id,
            "business": business,
            "email": email,
            "email_source": email_source,
            "confidence": confidence,
            "quality_score": quality_score
        })
        
        if verbose and idx % 50 == 0:
            print(f"   ✅ {idx}/{len(ranked_businesses)} - Found {email_found_count} emails")
    
    if verbose:
        print(f"\n✅ Scraping completed!\n")
    
    # Show summary
    if verbose:
        total_searched = len(ranked_businesses)
        if total_searched > 0:
            email_rate = (email_found_count / total_searched) * 100
            print("="*60)
            print("📊 SCRAPING SUMMARY")
            print("="*60)
            print(f"Total businesses found:     {len(businesses)}")
            print(f"Without websites:           {total_searched}")
            print(f"Emails discovered:          {email_found_count}")
            print(f"Email finding rate:         {email_rate:.1f}%")
            print(f"Ready for outreach:         {len(ready_for_outreach)}")
            print("="*60 + "\n")
    
    return (len(businesses), email_found_count, ready_for_outreach)


def main():
    parser = argparse.ArgumentParser(
        description="🔍 Web Scraper - Step 1: Find businesses and extract emails",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Business Types:
  restaurant           Search for restaurants
  solution_company     Search for software/IT companies
  hr_company           Search for HR/recruitment
  ecommerce            Search for e-commerce stores
  service_business     Search for service providers

Examples:
  python scraper.py                        # Scrape restaurants
  python scraper.py --type=solution_company # Scrape tech companies
  python scraper.py --type=hr_company      # Scrape HR companies
        """
    )
    
    parser.add_argument("--type", type=str, default="restaurant",
                       help="Business type to search for (default: restaurant)")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Run scraper
    total, emails_found, results = scrape_businesses(
        business_type=args.type,
        verbose=not args.quiet
    )
    
    print("\n🎯 Next Steps:")
    print("   1. Review results: python workflow.py --review")
    print("   2. Export to CSV:  python workflow.py --export")
    print("   3. Send emails:    python workflow.py --send-emails")
    print()


if __name__ == "__main__":
    main()
