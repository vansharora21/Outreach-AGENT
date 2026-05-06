# 🎯 Multi-Business Outreach: Quick Start Guide

Your agent now searches for **ANY TYPE OF BUSINESS**, not just restaurants!

## 🚀 Available Business Types

```bash
python cli.py --list-types
```

### Current Business Types:

1. **restaurant** (default)
   - Finds restaurants without websites
   - Targets: pizzerias, cafes, bars, diners

2. **solution_company**
   - Finds software/IT solution companies
   - Targets: tech startups, consulting firms, dev shops

3. **hr_company**
   - Finds HR/recruitment companies
   - Targets: staffing agencies, recruiting firms

4. **ecommerce**
   - Finds online stores and retail shops
   - Targets: e-commerce businesses

5. **service_business**
   - Finds service providers
   - Targets: plumbers, electricians, contractors

---

## 📖 Quick Start Examples

### Example 1: Find Restaurants (Default)

```bash
# Test mode first
python cli.py --initial --test

# Then go live
python cli.py --initial
```

### Example 2: Find Solution Companies

```bash
# Test mode
python cli.py --initial --type=solution_company --test

# Live
python cli.py --initial --type=solution_company
```

### Example 3: Find HR/Recruitment Companies

```bash
# Test mode
python cli.py --initial --type=hr_company --test

# Live
python cli.py --initial --type=hr_company
```

### Example 4: Find E-commerce Businesses

```bash
# Live
python cli.py --initial --type=ecommerce
```

### Example 5: Find Service Businesses

```bash
# Live
python cli.py --initial --type=service_business
```

---

## 🎨 Customize for Your Use Case

### Option 1: Modify Existing Type

Edit `search_config.py`:

```python
# Change restaurant patterns to target fine dining only
RESTAURANT_CONFIG = {
    "name": "restaurant",
    "search_terms": ["fine dining", "upscale restaurant", "luxury dining"],
    "priority_cuisines": ["french", "italian", "japanese"],
    "exclude_cuisines": ["fast_food", "pizza"],
    "email_patterns": [
        "reservations@{domain}",  # Changed!
        "contact@{domain}",
        "info@{domain}",
    ],
}
```

### Option 2: Create New Business Type

Add to `search_config.py`:

```python
# Medical Practice Configuration
MEDICAL_PRACTICE_CONFIG = {
    "name": "medical_practice",
    "search_terms": ["medical", "clinic", "doctor", "healthcare", "hospital"],
    "keywords": ["appointments", "clinic", "doctor", "medical"],
    "email_patterns": [
        "info@{domain}",
        "appointments@{domain}",
        "contact@{domain}",
        "hello@{domain}",
        "support@{domain}",
    ],
    "priority_keywords": ["healthcare", "clinic", "doctor"],
}

# Add to ALL_CONFIGS
ALL_CONFIGS = {
    "restaurant": RESTAURANT_CONFIG,
    # ... other types ...
    "medical_practice": MEDICAL_PRACTICE_CONFIG,  # NEW
}
```

Then use:

```bash
python cli.py --initial --type=medical_practice
```

---

## 📊 Workflow for Different Business Types

### For Solution Companies

```bash
# Find solution companies without websites
python cli.py --initial --type=solution_company --test

# View results
python cli.py --stats

# Send follow-ups after 3 days
python cli.py --followup --type=solution_company

# Export data for analysis
python cli.py --export
```

### For HR/Recruitment Agencies

```bash
# Search for HR companies
python cli.py --initial --type=hr_company --test

# Review top quality prospects
# Edit results/contacts_*.csv
# Look for established companies (quality_score > 80%)

# Send emails
python cli.py --initial --type=hr_company

# Schedule follow-ups
python cli.py --followup
```

### For E-commerce

```bash
# Find e-commerce without websites
python cli.py --initial --type=ecommerce

# Check email finding success rate
python cli.py --stats

# Export to CRM
python cli.py --export
```

---

## 🔍 Email Finding by Business Type

Different types have **different email patterns**:

### Restaurant Emails
```
info@pizzaplace.com (most common)
reservations@pizzaplace.com
orders@pizzaplace.com
contact@pizzaplace.com
```

### Solution Company Emails
```
sales@techco.com (most common)
business@techco.com
hello@techco.com
info@techco.com
contact@techco.com
```

### HR Company Emails
```
hr@staffing.com (most common)
recruitment@staffing.com
hiring@staffing.com
jobs@staffing.com
contact@staffing.com
```

**The agent automatically tries the most relevant patterns first!**

---

## 📈 Performance by Business Type

### Expected Email Finding Rates

| Type | Email Finding % | Avg Quality Score | Difficulty |
|------|-----------------|------------------|------------|
| Restaurant | 70-85% | 65% | Easy |
| Solution Company | 80-90% | 75% | Medium |
| HR Company | 75-85% | 70% | Medium |
| E-commerce | 75-80% | 68% | Medium |
| Service Business | 65-75% | 60% | Hard |

---

## 💡 Best Practices

### 1. Always Test First

```bash
python cli.py --initial --type=<type> --test
```

### 2. Check Success Rates

```bash
python cli.py --stats
# Look for email finding rate >= 80%
```

### 3. Export & Review

```bash
python cli.py --export
# Open CSV and review quality_score and email_source
```

### 4. Adjust Filters

```bash
# If too few found, try lowering quality_score threshold
# Edit utils/filter.py min_quality_score
```

### 5. Custom Email Patterns

```python
# If success rate is low for your type,
# add domain-specific email patterns
# Edit search_config.py
```

---

## 🎯 Multi-Type Campaign Example

Run campaigns for multiple business types:

```bash
# Week 1: Restaurants
python cli.py --initial --type=restaurant

# Week 2: Solution Companies
python cli.py --initial --type=solution_company

# Week 3: HR Companies
python cli.py --initial --type=hr_company

# Export everything
python cli.py --export
```

---

## 🚀 Advanced: Create Your Own Type

### Step 1: Research Target Domain

Find:
- Common search terms
- Typical email patterns
- Business keywords
- Industry classifications

### Step 2: Add to `search_config.py`

```python
YOUR_TYPE_CONFIG = {
    "name": "your_type",
    "search_terms": ["keyword1", "keyword2"],
    "keywords": ["relevant", "words"],
    "email_patterns": [
        "primary@{domain}",
        "secondary@{domain}",
    ],
    "priority_keywords": ["important"],
}

ALL_CONFIGS["your_type"] = YOUR_TYPE_CONFIG
```

### Step 3: Test

```bash
python cli.py --initial --type=your_type --test
```

### Step 4: Iterate

- Check success rate
- Refine patterns if needed
- Go live when satisfied

---

## 📋 Recommended Workflows

### B2B Lead Generation

```bash
# Find solution companies in your region
python cli.py --initial --type=solution_company

# 3 days later, follow up
python cli.py --followup

# 7 days later, final follow up
python cli.py --followup

# Export qualified leads
python cli.py --export
```

### Staffing/Recruitment

```bash
# Find HR companies
python cli.py --initial --type=hr_company

# Export to spreadsheet
python cli.py --export

# Manually review and prioritize
# Filter by quality_score in Excel

# Send personalized emails to top tier
```

### Local Service Marketing

```bash
# Find service businesses without websites
python cli.py --initial --type=service_business

# Export results
python cli.py --export

# Use CSV for Google Sheets campaign tracking
# Monitor responses
```

---

## ⚠️ Important Notes

### Email Finding Success Varies by Type

- **Easier**: Restaurants, e-commerce (usually have websites with email)
- **Harder**: Small service businesses (fewer online presence)

### Adjust Expectations

- Some types may have 65-75% success instead of 90%
- This is normal!
- Still much better than manual research

### Quality Scores Matter

- Higher quality_score = more likely to respond
- Sort by quality_score before sending
- Target top 50% first

---

## 🎓 Learning Resources

- [Email Finding Strategy](EMAIL_FINDING_STRATEGY.md) - Deep dive into how emails are found
- [Analytics Guide](results/README.md) - Understand the metrics
- [Main README](readme.md) - Full documentation

---

**Start with restaurants, master it, then expand to other types!** 🚀
