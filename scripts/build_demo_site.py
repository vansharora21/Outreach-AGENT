"""Build the privacy-safe static dashboard for Render deployment."""

from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
SOURCE = ROOT / "dashboard.html"

PORTFOLIO_SNAPSHOT = """window.dashboardData = {
  summary: {
    total_found: 139, emails_found: 85, emails_sent: 85,
    emails_opened: 52, emails_replied: 12, emails_bounced: 4,
    bounce_rate: 4.7, open_rate: 64.2, email_finding_rate: 61.2
  },
  email_source_breakdown: { data: [["website", 42], ["enrichment", 33], ["osm", 10]] },
  quality_distribution: { data: [["Excellent (0.8-1.0)", 32], ["Good (0.6-0.8)", 48], ["Fair (0.4-0.6)", 44], ["Poor (<0.4)", 15]] },
  top_contacts: [
    { name: "Sample Lead 01", email: "lead-01@demo.invalid", cuisine: "Restaurant", contact_quality_score: 0.90, email_source: "website" },
    { name: "Sample Lead 02", email: "lead-02@demo.invalid", cuisine: "Restaurant", contact_quality_score: 0.85, email_source: "website" },
    { name: "Sample Lead 03", email: "lead-03@demo.invalid", cuisine: "Service", contact_quality_score: 0.80, email_source: "osm" }
  ]
};
"""


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "results").mkdir(parents=True)
    shutil.copy2(SOURCE, DIST / "index.html")
    (DIST / "results" / "dashboard_data.js").write_text(PORTFOLIO_SNAPSHOT, encoding="utf-8")
    print(f"Built privacy-safe portfolio site in {DIST}")


if __name__ == "__main__":
    main()
