# Local PageSpeed → Google Sheets Logger (GHL Speed Testing)

This project runs locally on your machine and:
1) Calls the Google PageSpeed Insights API for a set of URLs
2) Appends a NEW ROW to a Google Sheet per test result (it does NOT write into fixed columns like “Column C” URLs)

This is ideal for:
- Page-by-page testing (even if your internal links are incomplete)
- Keeping a history of runs (timestamped results) without overwriting old data

---

## What you need before running

You will create:
- A Google Cloud project
- A PageSpeed Insights API key
- A Google service account + `creds.json` key for Google Sheets API access
- A Google Sheet with column headings (your script appends rows under those headings)

---

## 1) Create your Google Sheet (headings only)

Create a Google Sheet (any name). Add a header row in Row 1. Example headings:

- Timestamp
- URL
- Strategy (mobile/desktop)
- Performance Score
- LCP
- CLS
- TBT
- FCP (optional)
- Speed Index (optional)
- TTFB (optional)
- Total Requests (optional)
- Total Bytes (optional)
- Notes
- Error

Your exact headings can vary — the important part is:
✅ Row 1 is headers  
✅ Your script appends rows starting at Row 2

---

## 2) Get a PageSpeed Insights API key (Google Cloud)

You need an API key for the PageSpeed Insights API so your local script can call:

`https://www.googleapis.com/pagespeedonline/v5/runPagespeed`

### Step-by-step
1. Go to Google Cloud Console → APIs & Services
2. Create or select a project
3. Enable the API:
   - APIs & Services → Library
   - Search: **PageSpeed Insights API**
   - Click → **Enable**
4. Create an API key:
   - APIs & Services → Credentials
   - **Create Credentials → API key**
5. (Recommended) Restrict the key:
   - Click the created key
   - Under “API restrictions” → select **Restrict key**
   - Choose **PageSpeed Insights API**
   - Save

Notes:
- You usually do NOT need an OAuth flow for PageSpeed Insights; an API key is enough.
- If you hit quota/rate limits, add rate limiting and/or request more quota in Google Cloud.

---

## 3) Create `creds.json` for Google Sheets (Service Account)

This is the part most people get wrong. The reliable approach is a **service account** with a JSON key.

### 3.1 Enable Google Sheets API
1. Google Cloud Console → APIs & Services → Library
2. Search **Google Sheets API**
3. Click → **Enable**

(You typically do NOT need Google Drive API unless your script creates sheets or searches Drive.)

### 3.2 Create a Service Account
1. Google Cloud Console → IAM & Admin → **Service Accounts**
2. **Create Service Account**
   - Name: `sheets-speedtest-writer` (or anything)
   - Create and Continue
3. Assign permissions:
   - For most scripts, you do NOT need broad permissions.
   - You can skip roles entirely and rely on sharing the sheet with the service account email.
   - If Google forces a role, use something minimal like “Viewer” (not required for sheet editing if sharing is correct).

### 3.3 Create a JSON key file (this becomes `creds.json`)
1. Open the service account you created
2. Go to **Keys** tab
3. **Add Key → Create new key**
4. Choose **JSON**
5. Download the file
6. Rename it to `creds.json` and place it in your project root (same folder as the script)

⚠️ Treat `creds.json` like a password:
- NEVER commit it to git
- If it leaks, delete/rotate it in Google Cloud immediately

### 3.4 Share the Google Sheet with the service account
This is the critical step.

1. Open your Google Sheet
2. Click **Share**
3. Add the service account email (looks like):
   `sheets-speedtest-writer@YOUR_PROJECT.iam.gserviceaccount.com`
4. Give it **Editor** access
5. Save

If you don’t share it, your script will get “permission denied” even with valid creds.

---

## 4) Configure local secrets

This repo uses sensitive API keys you will have to fill in (not committed).

1) Copy your API key for PageSpeedInsights
2) Fill in towards the type of main.py where API_KEY = "" currently is.
3) Paste your creds.json into root of project, same directory where main.py and pages. txt live


### How to find Spreadsheet ID
From your sheet URL:
`https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/edit#gid=0`

Copy the `<SPREADSHEET_ID>` portion.

---

## 5) Set up page.txt file

Edit the urls line by line in the pages.txt file to include every url you want to be speed tested.

Make sure every seperate url is on a new line.

All urls for a site can easily be found from the sitemap.xml.


## 6) Run locally

Typical flow (example):
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py# PythonWebsiteSpeedTesting
