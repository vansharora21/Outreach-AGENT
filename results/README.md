# 📊 Results Export Folder

This folder contains all exported data from your restaurant outreach campaigns in CSV format.

## 📁 Files Generated

### `contacts_TIMESTAMP.csv`
**All restaurant contacts identified and ranked by quality**

Columns:
- `ID` - Unique contact ID
- `Name` - Restaurant name
- `Email` - Contact email address
- `Phone` - Restaurant phone number
- `Website` - Restaurant website (if available)
- `Cuisine` - Type of cuisine
- `Opening Hours` - Operating hours
- `Email Source` - Where email came from (osm/website/generated)
- `Email Confidence %` - How confident we are the email is correct (0-100%)
- `Quality Score %` - Overall quality of this prospect (0-100%)
- `Added Date` - When contact was first identified

**Use Cases:**
- Import into CRM (Salesforce, HubSpot)
- Create filtered lists (e.g., only Italian restaurants)
- Sort by quality score to find best prospects
- Follow up manually on high-quality contacts

---

### `campaigns_TIMESTAMP.csv`
**Record of all emails sent**

Columns:
- `Campaign ID` - Unique campaign ID
- `Restaurant Name` - Who received the email
- `Email` - Email address
- `Subject` - Email subject line
- `Status` - sent/failed/test_mode/bounced
- `Round` - Which outreach round (1=initial, 2=follow-up 1, etc)
- `Sent Date` - Timestamp when email was sent
- `Error Message` - If failed, why it failed

**Use Cases:**
- Track which emails were successfully sent
- Identify failed emails for retry
- See which cuisines/sources had highest send success
- Calculate delivery rates

---

### `engagement_TIMESTAMP.csv`
**Email interactions (opens, clicks, replies)**

Columns:
- `Tracking ID` - Unique tracking ID
- `Restaurant Name` - Which restaurant
- `Email` - Email address
- `Event Type` - opened/clicked/replied/bounced
- `Event Time` - When the event occurred
- `Details` - Additional details
- `Campaign Round` - Which round of outreach

**Use Cases:**
- See which emails got opened
- Track replies and conversations
- Identify engaged prospects
- Calculate open rates by cuisine/email source

---

### `do_not_contact_TIMESTAMP.csv`
**Unsubscribed or invalid contacts**

Columns:
- `ID` - Record ID
- `Email` - Email address
- `Phone` - Phone number
- `Reason` - Why they're on DNC (unsubscribed/invalid/no_response_3x)
- `Added Date` - When added to DNC list

**Use Cases:**
- Maintain compliance (GDPR/CAN-SPAM)
- Prevent duplicate outreach
- Track unsubscribes
- Share across teams

---

### `summary_report_TIMESTAMP.csv`
**High-level campaign overview and metrics**

Contains:
- Total contacts identified
- Total emails sent (successful/failed)
- Total replies received
- Reply rate percentage
- Top 5 cuisines by effectiveness
- Email source breakdown

**Use Cases:**
- Executive summary reports
- Dashboard metrics
- Performance tracking
- ROI calculation

---

## 🎯 How to Use These Files

### Option 1: Import into Excel/Google Sheets
```
1. Download the CSV file
2. Open Google Sheets or Excel
3. File → Import → Select CSV file
4. Create pivot tables, charts, filters
```

### Option 2: Analyze in Python
```python
import pandas as pd

# Load contacts
df = pd.read_csv('results/contacts_20240507_120000.csv')

# Filter high-quality Italian restaurants
italian = df[(df['Cuisine'] == 'Italian') & (df['Quality Score %'] >= 70)]
print(italian[['Name', 'Email', 'Quality Score %']])

# Export for manual follow-up
italian.to_csv('italian_restaurants_to_contact.csv', index=False)
```

### Option 3: Import into CRM
```
1. Open your CRM (Salesforce, HubSpot, Pipedrive)
2. Go to Import/Bulk Upload
3. Select CSV file
4. Map columns to CRM fields
5. Review and import
```

### Option 4: Create Charts in Google Sheets
```
1. Open summary_report_*.csv in Google Sheets
2. Select data
3. Insert → Chart
4. Choose pie chart for cuisine breakdown
5. Choose bar chart for email source comparison
```

---

## 📊 Sample Data Analysis

### Get Top 10 High-Quality Contacts
```python
import pandas as pd

df = pd.read_csv('results/contacts_20240507_120000.csv')
top_10 = df.nlargest(10, 'Quality Score %')
print(top_10[['Name', 'Email', 'Quality Score %', 'Cuisine']])
```

### Calculate Reply Rate by Cuisine
```python
contacts = pd.read_csv('results/contacts_20240507_120000.csv')
campaigns = pd.read_csv('results/campaigns_20240507_120000.csv')
engagement = pd.read_csv('results/engagement_20240507_120000.csv')

# Calculate rates...
```

### Export Specific Cuisine Group
```python
df = pd.read_csv('results/contacts_20240507_120000.csv')
italian = df[df['Cuisine'].str.contains('Italian', case=False, na=False)]
italian.to_csv('results/italian_restaurants.csv', index=False)
```

---

## 🔄 Automatic Export

By default, data is **automatically exported** after each campaign run:

```bash
python cli.py --initial
# ✅ Automatically exports: contacts, campaigns, summary

python cli.py --followup
# ✅ Automatically exports: updated campaigns, engagement

python cli.py --export
# Manually trigger export anytime
```

---

## 📅 File Naming

Files are timestamped so you can track multiple campaigns:

```
contacts_20240507_120000.csv      # May 7, 2024 @ 12:00:00
contacts_20240507_150000.csv      # May 7, 2024 @ 15:00:00
campaigns_20240508_090000.csv     # May 8, 2024 @ 09:00:00
```

Keep all files - they show your outreach history!

---

## 💡 Pro Tips

1. **Archive old files** - Keep results from each campaign run for historical analysis
2. **Use Google Sheets** - Import CSVs for easy sharing and collaboration
3. **Filter quality scores** - Focus follow-ups on quality_score >= 70%
4. **Track by cuisine** - See which cuisines convert best
5. **Monitor email sources** - Which finding method works best?
6. **Calculate ROI** - (Revenue from meetings / emails sent) × 100

---

## ⚠️ Data Privacy

- Keep these files secure - they contain personal contact information
- Respect do-not-contact list and unsubscribe requests
- Comply with GDPR/CAN-SPAM regulations
- Don't share without permission

---

**Need help?** Check the main README.md for more information!
