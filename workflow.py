"""
Workflow Manager: Orchestrate the complete outreach workflow
Step 1: Web scraping (find businesses & emails)
Step 2: Choose action (export or send emails)
Step 3: Execute (export data or send campaigns)
"""

import sys
import argparse
from scraper import scrape_businesses
from utils.database import init_database, get_campaign_stats
from utils.export import export_all_data, export_summary_report, export_contacts_to_csv
from agent import main as send_outreach_emails
from utils.followup import schedule_followups
from search_config import list_available_configs


def print_main_menu():
    """Print main workflow menu."""
    print("\n" + "="*60)
    print("🚀 MULTI-BUSINESS OUTREACH WORKFLOW")
    print("="*60)
    print("\n📋 Main Commands:")
    print("   python workflow.py --scrape                 Step 1: Find businesses & emails")
    print("   python workflow.py --export                 Step 2: Export to CSV")
    print("   python workflow.py --send-emails            Step 2: Send emails")
    print("   python workflow.py --review                 View scraping results")
    print("   python workflow.py --stats                  Campaign statistics")
    print("   python workflow.py --followup               Send follow-up emails")
    print("\n🎯 Business Types:")
    for btype in list_available_configs():
        print(f"   • {btype}")
    print("\n💡 Examples:")
    print("   # Full workflow")
    print("   python workflow.py --scrape                    # Find businesses")
    print("   python workflow.py --export                    # Export to CSV")
    print("   python workflow.py --send-emails               # Send emails")
    print("\n   # With business type")
    print("   python workflow.py --scrape --type=solution_company")
    print("   python workflow.py --send-emails --type=solution_company")
    print("\n   # Follow-ups")
    print("   python workflow.py --followup")
    print("="*60 + "\n")


def step1_scrape(business_type: str = "restaurant"):
    """Step 1: Web scraping - Find businesses and emails."""
    print("\n" + "="*70)
    print("⏱️  STEP 1: WEB SCRAPING - Finding businesses and extracting emails")
    print("="*70)
    
    total, emails_found, results = scrape_businesses(
        business_type=business_type,
        verbose=True
    )
    
    if not results:
        print("❌ No businesses found with emails. Try a different search.")
        return False
    
    return True


def step2_menu():
    """Step 2: Ask user what to do with results."""
    print("\n" + "="*70)
    print("⏱️  STEP 2: CHOOSE ACTION - What do you want to do with the results?")
    print("="*70)
    print("\n📋 Options:")
    print("   1️⃣  EXPORT to CSV       - Review results in spreadsheet")
    print("   2️⃣  SEND EMAILS         - Send campaign emails now")
    print("   3️⃣  VIEW RESULTS        - Show data in terminal")
    print("   4️⃣  CANCEL              - Don't do anything")
    
    print("\n👉 Choice: ", end="")
    choice = input().strip()
    
    return choice


def step3_export():
    """Step 3: Export data to CSV."""
    print("\n" + "="*70)
    print("⏱️  STEP 3: EXPORT - Exporting data to CSV files")
    print("="*70)
    print()
    
    files = export_all_data()
    summary_file = export_summary_report()
    
    print(f"\n✅ Export completed!")
    print(f"\n📁 Files saved to results/ folder:")
    for key, path in files.items():
        print(f"   ✓ {path}")
    print(f"   ✓ {summary_file}")
    print(f"\n💾 Total files: {len(files) + 1}")
    print(f"\n📊 Next: Open results/contacts_*.csv in Excel to review")
    print()


def step3_send_emails(business_type: str = "restaurant", test_mode: bool = False):
    """Step 3: Send emails."""
    print("\n" + "="*70)
    print("⏱️  STEP 3: EMAIL CAMPAIGN - Sending outreach emails")
    print("="*70)
    print()
    
    if test_mode:
        print("🧪 TEST MODE - No emails will be sent (dry run)")
        print()
    
    send_outreach_emails(
        business_type=business_type,
        test_mode=test_mode
    )
    
    print()


def step3_view_results():
    """Step 3: View results in terminal."""
    print("\n" + "="*70)
    print("⏱️  STEP 3: RESULTS - Viewing scraped data")
    print("="*70)
    print()
    
    stats = get_campaign_stats()
    
    print("📊 Campaign Statistics:")
    print("-" * 40)
    for key, value in stats.items():
        formatted_key = key.replace("_", " ").title()
        print(f"   {formatted_key}: {value}")
    print("-" * 40)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="🚀 Multi-Business Outreach Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Business Types:
  restaurant           Search for restaurants
  solution_company     Search for software/IT companies
  hr_company           Search for HR/recruitment
  ecommerce            Search for e-commerce stores
  service_business     Search for service providers

Complete Workflow:
  1. python workflow.py --scrape                  (Find businesses)
  2. python workflow.py --export                  (Review in CSV)
  3. python workflow.py --send-emails             (Send campaigns)

Quick Start:
  python workflow.py --scrape --type=restaurant
  python workflow.py --export
  python workflow.py --send-emails --type=restaurant

Follow-ups:
  python workflow.py --followup                   (Send day 3 follow-up)
  python workflow.py --followup                   (Send day 7 follow-up)
        """
    )
    
    # Step 1: Scraping
    parser.add_argument("--scrape", action="store_true",
                       help="Step 1: Find businesses and extract emails")
    
    # Step 2: Action
    parser.add_argument("--export", action="store_true",
                       help="Step 2: Export to CSV files")
    parser.add_argument("--send-emails", action="store_true",
                       help="Step 2: Send outreach emails")
    parser.add_argument("--review", action="store_true",
                       help="Step 2: View results in terminal")
    
    # Other commands
    parser.add_argument("--stats", action="store_true",
                       help="Show campaign statistics")
    parser.add_argument("--followup", action="store_true",
                       help="Send follow-up emails (Day 3 or Day 7)")
    
    # Options
    parser.add_argument("--type", type=str, default="restaurant",
                       help="Business type (default: restaurant)")
    parser.add_argument("--test", action="store_true",
                       help="Test mode (don't actually send emails)")
    parser.add_argument("--no-menu", action="store_true",
                       help="Skip menu selection, go direct to action")
    
    args = parser.parse_args()
    
    # Initialize database
    init_database()
    
    # No arguments = show menu
    if not any([args.scrape, args.export, args.send_emails, args.review, 
                args.stats, args.followup]):
        print_main_menu()
        return
    
    # Step 1: Scrape
    if args.scrape:
        success = step1_scrape(business_type=args.type)
        if not success:
            return
        
        if args.no_menu:
            print("\n✅ Scraping completed! Use --export or --send-emails next.\n")
            return
        
        # Ask user what to do
        choice = step2_menu()
        
        if choice == "1":
            step3_export()
        elif choice == "2":
            step3_send_emails(business_type=args.type, test_mode=args.test)
        elif choice == "3":
            step3_view_results()
        elif choice == "4":
            print("\n⏸️  Cancelled. Results saved in database for later.\n")
        else:
            print("\n❌ Invalid choice.\n")
    
    # Export
    elif args.export:
        step3_export()
    
    # Send emails
    elif args.send_emails:
        # Ask for confirmation
        print("\n" + "="*70)
        print("⚠️  SENDING EMAILS - This will send real emails!")
        print("="*70)
        print(f"\nBusiness type: {args.type}")
        if args.test:
            print("Mode: TEST (no emails will be sent)")
        else:
            print("Mode: LIVE (emails will be sent)")
        print("\nProceed? (yes/no): ", end="")
        
        confirm = input().strip().lower()
        if confirm in ["yes", "y"]:
            step3_send_emails(business_type=args.type, test_mode=args.test)
        else:
            print("Cancelled.\n")
    
    # Review
    elif args.review:
        step3_view_results()
    
    # Statistics
    elif args.stats:
        print("\n📊 CAMPAIGN STATISTICS")
        print("="*60)
        stats = get_campaign_stats()
        for key, value in stats.items():
            formatted_key = key.replace("_", " ").title()
            print(f"{formatted_key}: {value}")
        print("="*60 + "\n")
    
    # Follow-ups
    elif args.followup:
        print("\n🔄 FOLLOW-UP CAMPAIGN")
        print("="*60)
        print("Sending follow-up emails...\n")
        schedule_followups(test_mode=args.test)


if __name__ == "__main__":
    main()
