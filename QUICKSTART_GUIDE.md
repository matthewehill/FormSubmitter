# FormSubmitter - Quick Start Guide

## 🎯 Complete Setup in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to the project directory
cd /path/to/FormSubmitter

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

Wait for installation to complete (~300MB download for Chrome).

### Step 2: Configure Your Settings (1 minute)

```bash
# Copy the example configuration
cp .env.example .env
```

**Edit `.env` file and change these lines:**

```bash
YOUR_NAME=Matt                                    # Your first name
YOUR_EMAIL=matt@youremail.com                     # YOUR real email
YOUR_PHONE=555-123-4567                           # YOUR real phone

# For testing, use these settings:
HEADLESS=false                                    # See the browser
MAX_WORKERS=1                                     # One at a time
LOG_LEVEL=INFO                                    # See what's happening

# Stealth features (recommended)
RANDOMIZE_USER_AGENT=true
RANDOMIZE_VIEWPORT=true
EMULATE_HUMAN_BEHAVIOR=true
WEBDRIVER_DETECTION_EVASION=true

# Leave these as false for now
USE_PROXIES=false
PROXY_ROTATION=false

# Only add if sites have CAPTCHAs (costs money)
CAPTCHA_API_KEY=                                  # Leave empty for now
```

### Step 3: Create Your Website List (1 minute)

Create a file called `contacts.csv`:

```csv
business_name,website_url,city
ABC Company,https://example.com,Denver
XYZ Business,https://test-site.com,Boulder
```

**Real world example:**

```csv
business_name,website_url,city
Joe's Plumbing,https://joesplumbing.com,Phoenix
ABC HVAC,https://abchvac.com,Denver
Best Heating,https://bestheating.net,Seattle
Quality Air,https://qualityair.com,Austin
Elite Cooling,https://elitecooling.com,Miami
```

**Tips:**
- Add as many websites as you want (one per line)
- Always include `https://` in the URL
- First line MUST be the header
- No spaces around commas

### Step 4: Run Your First Test (1 minute)

```bash
# Test with ONE website first
python main.py --mode sequential
```

**What you'll see:**
- Browser window opens
- Navigates to first website
- Looks for contact form
- Fills out the form
- Submits it
- Shows success/failure

**Watch the terminal for logs:**

```
================================================================================
Contact Form Automation Tool
================================================================================
Mode: Sequential
Headless: False
Max Workers: 1
================================================================================

Processing: ABC Company | https://example.com | Denver
Navigating to: https://example.com
Searching for contact form...
Found form on current page
Filling form fields...
✓ Form filled successfully
No captcha detected on page
Clicking submit button...
✓ Successfully submitted form for ABC Company
```

### Step 5: Run in Production Mode

Once you've tested and it works:

**1. Edit `.env` to run headless (faster):**

```bash
HEADLESS=true                # Browser runs invisibly
MAX_WORKERS=3                # Process 3 sites at once
```

**2. Run in parallel mode:**

```bash
python main.py --mode parallel
```

**3. It will process all sites in your CSV file!**

## 📊 Checking Progress

### View Statistics

```bash
python main.py --stats
```

Output:
```
================================================================================
FINAL STATISTICS
================================================================================
Total Processed: 45
Successful: 38
Failed: 7
Success Rate: 84.4%
Started At: 2024-01-15 10:30:00
Last Updated: 2024-01-15 12:45:30
================================================================================
```

### View Logs

```bash
# View latest log file
ls -lt logs/

# View specific log
tail -f logs/automation_*.log

# View submissions CSV
cat logs/submissions.csv
```

### Resume After Interruption

The tool automatically saves progress! If it stops (crash, Ctrl+C, etc.), just run again:

```bash
python main.py
```

It will **skip already processed sites** and continue where it left off.

## 🔧 Common Issues & Solutions

### Issue 1: "No module named 'playwright'"

**Solution:**
```bash
pip install -r requirements.txt
playwright install chromium
```

### Issue 2: "Configuration errors: YOUR_EMAIL is required"

**Solution:**
- Make sure you created `.env` file (copy from `.env.example`)
- Edit `.env` and fill in YOUR_EMAIL and YOUR_PHONE

### Issue 3: "CSV file not found"

**Solution:**
```bash
# Make sure contacts.csv exists
ls contacts.csv

# If not, create it:
touch contacts.csv
# Then edit it with your websites
```

### Issue 4: "No contact form found" on most sites

**Solutions:**
1. Run in visible mode to see what's happening: `HEADLESS=false`
2. Increase timeout: `PAGE_LOAD_TIMEOUT=60`
3. Some sites may not have contact forms on homepage - that's normal

### Issue 5: Browser doesn't open

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

## 🎓 Understanding the CSV Format

The CSV file is how you tell the tool which websites to target.

### Required Format

```csv
business_name,website_url,city
Company Name,https://website.com,City Name
```

### Example with 10 Sites

```csv
business_name,website_url,city
ABC Heating & Cooling,https://abchvac.com,Denver
XYZ Plumbing Services,https://xyzplumbing.com,Phoenix
Best HVAC Company,https://besthvac.net,Seattle
Quality Air Solutions,https://qualityair.com,Austin
Elite Cooling Systems,https://elitecooling.com,Miami
Perfect Temperature,https://perfecttemp.com,Dallas
Climate Control Pro,https://climatecontrol.com,Houston
Superior Heating,https://superiorheating.com,Chicago
Premium Air Care,https://premiumair.com,Boston
Comfort Zone HVAC,https://comfortzone.com,Atlanta
```

### Rules

✅ **DO:**
- Include header row (first line)
- Use HTTPS URLs
- One website per line
- Keep it simple (no special characters in business names)

❌ **DON'T:**
- Add spaces around commas
- Forget the header row
- Use HTTP instead of HTTPS (use HTTPS)
- Leave empty lines

## 🚀 Advanced Usage

### Maximum Stealth Mode

Edit `.env`:

```bash
# Turn on ALL stealth features
RANDOMIZE_VIEWPORT=true
RANDOMIZE_USER_AGENT=true
EMULATE_HUMAN_BEHAVIOR=true
WEBDRIVER_DETECTION_EVASION=true

# Enable proxies (optional)
USE_PROXIES=true
PROXY_ROTATION=true

# Slower but more human-like
MIN_DELAY=10
MAX_DELAY=30
```

### Process Large Lists

For 100+ websites:

```bash
# Increase workers
MAX_WORKERS=5

# Run in headless mode (faster)
HEADLESS=true

# Let it run overnight
nohup python main.py --mode parallel > output.log 2>&1 &
```

### Retry Failed Submissions

After a run, retry only the failed ones:

```bash
python main.py --retry-failed
```

## 📈 Pro Tips

1. **Start small**: Test with 5-10 websites first
2. **Use visible mode** first (`HEADLESS=false`) to debug
3. **Check logs** in `logs/` directory for detailed info
4. **Sequential mode** is better for debugging
5. **Parallel mode** is faster for production
6. **Save progress** happens automatically
7. **CAPTCHA costs money** ($2-3 per 1000 solves on 2captcha.com)

## 🎯 Example Complete Workflow

```bash
# 1. Setup
pip install -r requirements.txt
playwright install chromium
cp .env.example .env

# 2. Edit .env with your email/phone

# 3. Create contacts.csv with your websites

# 4. Test with one site
python main.py --mode sequential

# 5. If it works, run all sites
python main.py --mode parallel

# 6. Check results
python main.py --stats
cat logs/submissions.csv

# 7. Retry any failures
python main.py --retry-failed
```

## 🆘 Need Help?

1. Check logs: `logs/automation_*.log`
2. Run in visible mode: `HEADLESS=false`
3. Run sequential mode: `--mode sequential`
4. Check CSV format (no spaces, proper header)
5. Verify .env has YOUR_EMAIL and YOUR_PHONE

---

**You're ready to go!** 🚀

Start with a small test (5 websites), make sure it works, then scale up!
