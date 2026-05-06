# 📁 Core Folder - Workflow Engines

## Purpose
**Main entry points and workflow orchestration** - These files contain the primary logic that runs campaigns.

## Files in This Folder

### 🎬 `workflow.py` (START HERE!)
**The main entry point for all operations**

**What it does:**
- Orchestrates the 3-step workflow (scrape → choose action → execute)
- Handles user menu selection
- Calls scraper.py, agent.py, or export functions

**When to use:**
```bash
python core/workflow.py --scrape              # Step 1: Find businesses
python core/workflow.py --export              # Step 2: Export data
python core/workflow.py --send-emails         # Step 2: Send campaigns
python core/workflow.py --stats               # View statistics
```

**Don't edit this** unless you want to change the workflow process itself.

---

### 🔍 `scraper.py`
**Step 1: Finds businesses and extracts email addresses**

**What it does:**
1. Queries OpenStreetMap for businesses
2. Filters by criteria (website, quality, type)
3. Uses 5 strategies to find email addresses
4. Saves results to SQLite database

**Key function:**
```python
def scrape_businesses(business_type: str = "restaurant", verbose: bool = True):
    # Returns (total_found, emails_found, ready_for_outreach)
```

**When to edit:**
- Change search radius (line ~50)
- Adjust filtering criteria (line ~60)
- Modify email finding logic (imports from `utils/email_finder.py`)

---

### ✉️ `agent.py`
**Sends email campaigns**

**What it does:**
1. Gets contacts from database
2. Generates personalized emails using OpenAI
3. Sends via Gmail SMTP
4. Logs all activities to database

**Key function:**
```python
def send_outreach_emails(business_type: str, test_mode: bool):
    # Sends emails to all ready contacts
```

**When to edit:**
- Change email generation logic
- Modify send rate limits
- Add new email templates

---

## 🔄 Data Flow

```
workflow.py (entry point)
    ↓
User chooses action:
    ├─→ --scrape     → scraper.py → email_finder.py → database.py
    ├─→ --export     → export.py → database.py → CSV files
    └─→ --send-emails → agent.py → ai_email.py → email_sender.py

Results saved to:
    ├─ data/agent.db (SQLite)
    └─ results/*.csv (CSV files)
```

---

## 💡 Tips for Users

**Running workflow:**
```bash
# Development/testing
python core/workflow.py --scrape --type=restaurant --test

# Production
python core/workflow.py --scrape --type=restaurant
```

**Common issues:**
- ❌ "No businesses found" → Check LOCATION_COORDS in .env
- ❌ "Gmail error" → Use App Password, not regular password
- ❌ "No emails found" → Lower min_quality_score or add API keys

---

## 🔧 Dependencies

Each file imports from:
- `config.py` - Environment variables
- `utils/search.py` - OpenStreetMap queries
- `utils/filter.py` - Filtering logic
- `utils/email_finder.py` - Email discovery
- `utils/database.py` - SQLite operations
- `utils/ai_email.py` - OpenAI integration
- `utils/export.py` - CSV export

---

## 📊 Expected Output

### After `--scrape`:
```
✅ Found 1000 businesses
✅ 300 businesses have NO website
📧 Finding contact emails...

✅ Pizza Palace
   Email: info@pizzapalace.com
   Source: website | Confidence: 75%
   Quality: 85%

📊 EMAIL FINDING RATE: 88.5% (265/300)
```

### After `--export`:
```
✅ Export completed!
📁 Files saved to results/ folder:
   ✓ results/contacts_20240507_120000.csv
   ✓ results/campaigns_20240507_120000.csv
   ✓ results/engagement_20240507_120000.csv
   ✓ results/do_not_contact_20240507_120000.csv
   ✓ results/summary_report_20240507_120000.csv
```

---

**Next:** Read [ARCHITECTURE.md](../ARCHITECTURE.md) for complete overview
