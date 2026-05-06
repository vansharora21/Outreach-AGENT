# 🏗️ Codebase Architecture Guide

## 📁 Folder Structure

```
RESTAURANT AGENT/
│
├── 📁 core/                          👈 Main workflow engines
│   ├── workflow.py                  Main entry point (3-step process)
│   ├── scraper.py                   Step 1: Web scraping & email finding
│   ├── agent.py                     Email sending logic
│   └── README.md                    Folder documentation
│
├── 📁 config/                        👈 Configuration & settings
│   ├── config.py                    Environment variables (.env)
│   ├── search_config.py             Business type configurations
│   └── README.md                    Folder documentation
│
├── 📁 utils/                         👈 Helper functions & utilities
│   ├── email_finder.py              Multi-step email discovery
│   ├── email_sender.py              Gmail SMTP integration
│   ├── search.py                    OpenStreetMap API queries
│   ├── filter.py                    Business filtering & ranking
│   ├── database.py                  SQLite database management
│   ├── ai_email.py                  Outreach message generation module
│   ├── export.py                    CSV export functionality
│   ├── followup.py                  Follow-up automation
│   ├── logger.py                    Legacy logging
│   └── README.md                    Folder documentation
│
├── 📁 data/                          👈 Data storage
│   ├── contacts.csv                 Sample data
│   ├── agent.db                     SQLite database (auto-created)
│   └── README.md                    Folder documentation
│
├── 📁 results/                       👈 Output & exports
│   ├── contacts_*.csv               Exported contacts
│   ├── campaigns_*.csv              Sent campaigns
│   ├── engagement_*.csv             Email tracking
│   ├── do_not_contact_*.csv         Unsubscribes
│   ├── summary_report_*.csv         Campaign summary
│   └── README.md                    Folder documentation
│
├── 📁 docs/                          👈 Documentation & guides
│   ├── QUICK_START.md               Get started in 5 minutes
│   ├── EMAIL_FINDING_STRATEGY.md    How emails are discovered
│   ├── MULTI_BUSINESS_GUIDE.md      Using different business types
│   ├── DATABASE_SCHEMA.md           SQLite table structure
│   ├── API_KEYS.md                  Setting up API keys
│   └── TROUBLESHOOTING.md           Common issues & fixes
│
├── requirements.txt                 Python dependencies
├── .env.example                     Example environment file
├── README.md                        👈 START HERE (main guide)
├── ARCHITECTURE.md                  👈 This file
└── cli.py                           CLI interface (deprecated, use workflow.py)
```

---

## 🎯 Each Folder's Purpose

### 📁 **`core/`** - Main Workflow Engines
**Purpose:** Contains the main entry points and workflow orchestration

| File | Purpose |
|------|---------|
| **workflow.py** | 🎬 Main entry point - orchestrates the 3-step workflow |
| **scraper.py** | 🔍 Step 1: Finds businesses & emails from OpenStreetMap |
| **agent.py** | ✉️ Step 2/3: Sends emails (called by workflow.py) |

**When to use:**
```bash
python core/workflow.py --scrape        # Step 1: Find businesses
python core/workflow.py --export         # Step 2: Export to CSV
python core/workflow.py --send-emails    # Step 3: Send campaigns
```

---

### 📁 **`config/`** - Configuration & Settings
**Purpose:** All configuration files in one place

| File | Purpose |
|------|---------|
| **config.py** | 🔐 Loads environment variables from .env |
| **search_config.py** | 🏢 Business type definitions (restaurant, hr, tech, etc) |

**How it works:**
```python
# config.py loads from .env file
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# search_config.py defines business types
RESTAURANT_CONFIG = {
    "search_terms": ["restaurant", "pizza", "cafe"],
    "email_patterns": ["info@", "reservations@"]
}
```

**When to customize:**
- Edit `.env` to add API keys
- Edit `search_config.py` to add business types

---

### 📁 **`utils/`** - Helper Functions & Utilities
**Purpose:** Reusable functions used by core modules

| File | Purpose |
|------|---------|
| **email_finder.py** | 🎯 Multi-step email discovery system (main file!) |
| **email_sender.py** | 📧 Gmail SMTP email sending |
| **search.py** | 🗺️ OpenStreetMap API queries |
| **filter.py** | 🧹 Filter & rank businesses by quality |
| **database.py** | 💾 SQLite database operations |
| **ai_email.py** | ✉️ Generate outreach messages |
| **export.py** | 📊 Export data to CSV |
| **followup.py** | 🔄 Send follow-up campaigns |

**Key file - email_finder.py:**
```python
# 5 strategies in priority order:
1. Website scraping (70-90%)
2. Clearbit API (95%)
3. Hunter.io API (80-95%)
4. Email patterns (50-60%)
5. OSM data (80%)
```

---

### 📁 **`data/`** - Data Storage
**Purpose:** Local data storage (database and sample files)

| File | Purpose |
|------|---------|
| **agent.db** | 🗄️ SQLite database (auto-created on first run) |
| **contacts.csv** | 📋 Sample contact data |

**Database tables:**
- `contacts` - Business info, email, quality score
- `campaigns` - Sent emails, status, results
- `email_tracking` - Opens, clicks, replies
- `do_not_contact` - Unsubscribes

---

### 📁 **`results/`** - Output & Exports
**Purpose:** All exported CSV files go here (auto-created on export)

| File | Purpose |
|------|---------|
| **contacts_*.csv** | ✅ All businesses with emails & quality scores |
| **campaigns_*.csv** | 📧 All sent emails & delivery status |
| **engagement_*.csv** | 📊 Opens, clicks, replies tracking |
| **do_not_contact_*.csv** | 🚫 Unsubscribes & bounces |
| **summary_report_*.csv** | 📈 Campaign summary & statistics |

**Use cases:**
- Import into CRM (Salesforce, HubSpot)
- Analyze in Excel/Google Sheets
- Track follow-up rates

---

### 📁 **`docs/`** - Documentation & Guides
**Purpose:** All guides and documentation

| File | Purpose |
|------|---------|
| **QUICK_START.md** | ⚡ Get started in 5 minutes |
| **EMAIL_FINDING_STRATEGY.md** | 🎯 How emails are discovered |
| **MULTI_BUSINESS_GUIDE.md** | 🏢 Use different business types |
| **DATABASE_SCHEMA.md** | 🗄️ Database table structures |
| **API_KEYS.md** | 🔑 Setup optional lookup services |
| **TROUBLESHOOTING.md** | 🐛 Fix common errors |

---

## 🚀 How Data Flows

### The 3-Step Workflow

```
┌─────────────────────────────────────────────────────┐
│ STEP 1: WEB SCRAPING (scraper.py)                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  OpenStreetMap API                                  │
│         ↓                                           │
│  Find businesses (restaurants, tech, HR)            │
│         ↓                                           │
│  Filter: only without websites                      │
│         ↓                                           │
│  Multi-strategy email finding:                      │
│    • Website scraping                               │
│    • Clearbit API                                   │
│    • Hunter.io API                                  │
│    • Email patterns                                 │
│    • OSM data                                       │
│         ↓                                           │
│  Calculate quality score                            │
│         ↓                                           │
│  Save to SQLite database                            │
│                                                     │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ STEP 2: CHOOSE ACTION (workflow.py menu)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  User chooses:                                      │
│  1. Export to CSV (review in Excel)                 │
│  2. Send emails (launch campaigns)                  │
│  3. View in terminal                                │
│  4. Cancel                                          │
│                                                     │
└─────────────────────────────────────────────────────┘
                          ↓
     ┌────────────────────┴────────────────────┐
     ↓                                         ↓
┌─────────────────────┐          ┌─────────────────────┐
│ STEP 3A: EXPORT     │          │ STEP 3B: EMAIL      │
│ (export.py)         │          │ (agent.py)          │
├─────────────────────┤          ├─────────────────────┤
│                     │          │                     │
│ Export to CSV:      │          │ Generate emails:    │
│ • contacts_*.csv    │          │ (using templates)   │
│ • campaigns_*.csv   │          │        ↓            │
│ • engagement_*.csv  │          │ Send via Gmail      │
│ • summary_*.csv     │          │        ↓            │
│        ↓            │          │ Log in database     │
│ Review in Excel     │          │        ↓            │
│        ↓            │          │ Schedule follow-ups │
│ Import to CRM       │          │        ↓            │
│                     │          │ Track engagement    │
└─────────────────────┘          │                     │
                                 └─────────────────────┘
```

---

## 🔄 Module Dependencies

```
workflow.py (entry point)
    ├── scraper.py
    │   ├── utils/search.py (OpenStreetMap)
    │   ├── utils/filter.py (ranking)
    │   ├── utils/email_finder.py (5 strategies)
    │   └── utils/database.py (save results)
    │
    ├── export.py
    │   └── utils/database.py (read from DB)
    │
    ├── agent.py
    │   ├── utils/database.py (get contacts)
    │   ├── utils/ai_email.py (message templates)
    │   ├── utils/email_sender.py (Gmail)
    │   └── utils/database.py (log campaign)
    │
    └── followup.py
        ├── utils/database.py
        ├── utils/ai_email.py
        └── utils/email_sender.py

config.py (used everywhere)
    └── search_config.py (business types)
```

---

## 📊 Database Schema (Simplified)

```
SQLite (agent.db)
│
├── contacts
│   ├── id, name, email, phone, website
│   ├── email_source (osm/website/clearbit/hunter/generated)
│   ├── confidence_score (0.0-1.0)
│   └── quality_score (0-100%)
│
├── campaigns
│   ├── id, contact_id, subject, body, status
│   ├── email_source
│   ├── sent_at, error
│   └── round (1, 2, 3 = initial, 3-day, 7-day)
│
├── email_tracking
│   ├── campaign_id, event_type (open/click/reply/bounce)
│   └── event_time
│
└── do_not_contact
    ├── email, phone, reason
    └── created_at
```

---

## 🎯 Quick Reference: What to Edit

| Task | File to Edit |
|------|-------------|
| Add API keys | `.env` (create from `.env.example`) |
| Change location | `config.py` - `LOCATION_COORDS` |
| Add business type | `config/search_config.py` |
| Customize email templates | `utils/ai_email.py` |
| Change Gmail account | `.env` - `EMAIL_ADDRESS` |
| Modify quality scoring | `utils/filter.py` |
| Add email patterns | `config/search_config.py` |

---

## 🚀 Next Steps

1. **Read QUICK_START.md** in `/docs` to run your first campaign
2. **Check API_KEYS.md** if you want free email APIs (Clearbit, Hunter)
3. **Review MULTI_BUSINESS_GUIDE.md** to target different businesses
4. **Start with:** `python core/workflow.py --scrape --type=restaurant`

---

**Architecture created for clarity and scalability!** 🎉
