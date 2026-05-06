"""
CLI tool for managing the outreach agent.
Provides commands for different operations and business types.
"""

import sys
import argparse
from utils.database import init_database, get_campaign_stats
from utils.export import export_all_data, export_summary_report
from agent import main as run_initial_outreach
from utils.followup import schedule_followups
from search_config import list_available_configs


def print_menu():
    """Print CLI menu."""
    print("\n" + "="*60)
    print("🎯 MULTI-BUSINESS OUTREACH AGENT CLI")
    print("="*60)
    print("\nMain Commands:")
    print("  1. python cli.py --initial              Start initial outreach")
    print("  2. python cli.py --followup             Send follow-up emails")
    print("  3. python cli.py --stats                Show campaign statistics")
    print("  4. python cli.py --export               Export all data to CSV")
    print("  5. python cli.py --init-db              Initialize database")
    print("  6. python cli.py --list-types           List available business types")
    print("\nBusiness Types (use with --type=):")
    for btype in list_available_configs():
        print(f"  • {btype}")
    
    print("\nExamples:")
    print("  python cli.py --initial --test")
    print("  python cli.py --initial --type=restaurant")
    print("  python cli.py --initial --type=solution_company")
    print("  python cli.py --initial --type=hr_company --test")
    print("  python cli.py --followup --type=restaurant")
    print("  python cli.py --export")
    print("  python cli.py --stats")
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="🎯 Multi-Business Outreach Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Business Types:
  restaurant           Search for restaurants (default)
  solution_company     Search for software/IT solution companies
  hr_company           Search for HR/recruitment companies
  ecommerce            Search for e-commerce businesses
  service_business     Search for service businesses (plumber, electrician, etc)

Examples:
  python cli.py --initial --test
  python cli.py --initial --type=restaurant
  python cli.py --initial --type=solution_company
  python cli.py --followup --type=hr_company
  python cli.py --export
        """
    )
    
    parser.add_argument("--initial", action="store_true", help="Run initial outreach campaign")
    parser.add_argument("--followup", action="store_true", help="Send follow-up emails")
    parser.add_argument("--stats", action="store_true", help="Show campaign statistics")
    parser.add_argument("--export", action="store_true", help="Export all data to CSV files")
    parser.add_argument("--init-db", action="store_true", help="Initialize database")
    parser.add_argument("--list-types", action="store_true", help="List available business types")
    parser.add_argument("--test", action="store_true", help="Test mode (don't send emails)")
    parser.add_argument("--type", type=str, default="restaurant", 
                       help="Business type to search for (default: restaurant)")
    
    args = parser.parse_args()
    
    # Initialize database
    if args.init_db or args.initial or args.followup or args.export or args.stats:
        init_database()
    
    # Show menu if no arguments
    if not any([args.initial, args.followup, args.stats, args.export, args.init_db, args.list_types]):
        print_menu()
        parser.print_help()
        return
    
    # List available business types
    if args.list_types:
        print("\n📋 Available Business Types:")
        print("="*40)
        for btype in list_available_configs():
            print(f"  • {btype}")
        print("="*40)
        print("\nUsage: python cli.py --initial --type=<business_type>")
        print("Example: python cli.py --initial --type=solution_company\n")
        return
    
    # Initial outreach
    if args.initial:
        print(f"\n🚀 Starting {args.type.replace('_', ' ')} outreach campaign...\n")
        run_initial_outreach(test_mode=args.test, business_type=args.type)
    
    # Follow-ups
    if args.followup:
        print(f"\n🔄 Starting follow-up campaign ({args.type.replace('_', ' ')})...\n")
        schedule_followups(test_mode=args.test)
    
    # Statistics
    if args.stats:
        print("\n📊 CAMPAIGN STATISTICS")
        print("="*40)
        stats = get_campaign_stats()
        for key, value in stats.items():
            formatted_key = key.replace("_", " ").title()
            print(f"{formatted_key}: {value}")
        print("="*40 + "\n")
    
    # Export data
    if args.export:
        print("\n📊 Exporting all data to CSV...\n")
        files = export_all_data()
        summary_file = export_summary_report()
        
        print(f"\n✅ Export completed!")
        print(f"\n📁 Files saved to results/ folder:")
        for key, path in files.items():
            print(f"   ✓ {path}")
        print(f"   ✓ {summary_file}")
        print(f"\n💾 Total files: {len(files) + 1}\n")


if __name__ == "__main__":
    main()
