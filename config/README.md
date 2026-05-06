# ⚙️ Config Folder - Configuration & Settings

## Purpose
**All configuration and business type definitions** - Centralized place for settings.

## Files in This Folder

### 🔐 `config.py`
**Loads environment variables from `.env` file**

**What it contains:**
```python
# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Location for searching
LOCATION_COORDS = os.getenv("LOCATION_COORDS")  # "40.7128,-74.0060"

# Search radius
SEARCH_RADIUS = 3000  # meters
```

**When to edit:**
1. Change default location (line ~20)
2. Change search radius
3. Change rate limits (e.mail sending speed)
4. Add new configuration values

**Important:**
- Don't add API keys here!
- Use `.env` file instead
- Keep sensitive data out of this file

---

### 🏢 `search_config.py`
**Business type definitions with email patterns**

**What it contains:**
```python
RESTAURANT_CONFIG = {
    "name": "restaurant",
    "search_terms": ["restaurant", "pizza", "cafe"],
    "keywords": ["cuisine", "dining"],
    "email_patterns": [
        "info@{domain}",
        "reservations@{domain}",
        "contact@{domain}",
    ]
}

SOLUTION_COMPANY_CONFIG = {
    "name": "solution_company",
    "search_terms": ["software", "technology", "consulting"],
    "email_patterns": [
        "sales@{domain}",
        "business@{domain}",
        "info@{domain}",
    ]
}

# ... more types ...
```

**Available business types:**
1. **restaurant** - Find restaurants
2. **solution_company** - Tech/software companies
3. **hr_company** - HR/recruitment agencies
4. **ecommerce** - Online stores
5. **service_business** - Plumbers, electricians, etc.

**When to edit:**
1. ✏️ Modify email patterns (try new variations)
2. ✏️ Add keywords (change what to search for)
3. ✏️ Add new business type

---

## 🚀 How to Add Your Own Business Type

### Step 1: Create Configuration
Edit `search_config.py`:

```python
# Add at the end of the file
DENTAL_OFFICE_CONFIG = {
    "name": "dental_office",
    "search_terms": ["dental office", "dentist", "orthodontist"],
    "keywords": ["dental", "clinic", "appointments"],
    "email_patterns": [
        "appointments@{domain}",
        "info@{domain}",
        "contact@{domain}",
        "hello@{domain}",
    ]
}
```

### Step 2: Register It
Add to `ALL_CONFIGS` dictionary (bottom of file):

```python
ALL_CONFIGS = {
    "restaurant": RESTAURANT_CONFIG,
    "solution_company": SOLUTION_COMPANY_CONFIG,
    "hr_company": HR_COMPANY_CONFIG,
    "ecommerce": ECOMMERCE_CONFIG,
    "service_business": SERVICE_BUSINESS_CONFIG,
    "dental_office": DENTAL_OFFICE_CONFIG,  # NEW!
}
```

### Step 3: Use It
```bash
python core/workflow.py --scrape --type=dental_office
```

---

## 📝 Configuration Fields Explained

| Field | Purpose | Example |
|-------|---------|---------|
| `name` | Unique identifier | `"restaurant"` |
| `search_terms` | What to search for | `["pizza", "cafe"]` |
| `keywords` | Filter keywords | `["cuisine", "dining"]` |
| `email_patterns` | Pattern combinations | `["info@", "sales@"]` |

---

## 🎯 Tips for Email Patterns

**Good patterns (high confidence):**
- `info@{domain}` - Most common
- `contact@{domain}` - Very common
- `sales@{domain}` - For B2B

**Medium patterns:**
- `hello@{domain}`
- `support@{domain}`

**Risky patterns (low confidence):**
- `business@{domain}` - Might not exist
- `help@{domain}` - Generic

---

## 🔧 Environment Variables (`.env` file)

Create `.env` with:

```env
# Required
OPENAI_API_KEY=sk_xxx...
EMAIL_ADDRESS=your@gmail.com
EMAIL_PASSWORD=app_password_here
LOCATION_COORDS=40.7128,-74.0060

# Optional
CLEARBIT_API_KEY=your_key
HUNTER_API_KEY=your_key
```

**Don't commit `.env` to git!** (it's in `.gitignore`)

---

## 🗂️ File Locations

```
config/
├── config.py              ← Load environment
├── search_config.py       ← Business type definitions
└── README.md             ← This file
```

---

## 💡 Pro Tips

1. **Test first:** Always test new business type with `--test` flag
2. **Email patterns matter:** Better patterns = higher email finding rate
3. **Add local knowledge:** Include local search terms for your region
4. **Track results:** Note which email patterns work best

Example:
```bash
# Test dental offices
python core/workflow.py --scrape --type=dental_office --test

# If good results, go live
python core/workflow.py --scrape --type=dental_office
```

---

## 📊 Example: Custom Configuration

**Goal:** Search for yoga studios

```python
# Add to search_config.py
YOGA_STUDIO_CONFIG = {
    "name": "yoga_studio",
    "search_terms": [
        "yoga",
        "yoga studio",
        "yoga class",
        "meditation center"
    ],
    "keywords": [
        "yoga",
        "wellness",
        "fitness",
        "classes"
    ],
    "email_patterns": [
        "contact@{domain}",
        "info@{domain}",
        "classes@{domain}",
        "hello@{domain}",
    ]
}

# Register it
ALL_CONFIGS["yoga_studio"] = YOGA_STUDIO_CONFIG
```

**Use it:**
```bash
python core/workflow.py --scrape --type=yoga_studio
```

---

## 🐛 Troubleshooting

### ❌ "Business type not found"
- Check if added to `ALL_CONFIGS`
- Restart Python

### ❌ "No emails found"
- Add more email patterns
- Use API keys (Clearbit, Hunter)
- Check if websites actually have emails

### ❌ "Wrong search results"
- Adjust `search_terms`
- Add/remove `keywords`
- Check OpenStreetMap tags for business type

---

**Next:** Read [ARCHITECTURE.md](../ARCHITECTURE.md) for complete overview
