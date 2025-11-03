# Quick Start Guide

Get up and running in 5 minutes!

## 1. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Install Playwright browser
- Create .env and contacts.csv from templates

## 2. Configure Your Settings

Edit `.env` file:

```bash
nano .env
```

**Required fields:**
```env
YOUR_EMAIL=your.email@example.com
YOUR_PHONE=555-123-4567
```

**Optional but recommended:**
```env
CAPTCHA_API_KEY=your_2captcha_key  # Get from https://2captcha.com
MAX_WORKERS=3                       # Number of parallel browsers
```

## 3. Add Your Contacts

Edit `contacts.csv`:

```bash
nano contacts.csv
```

Format:
```csv
business_name,website_url,city
ABC Heating,https://abchvac.com,Denver
XYZ Cooling,https://xyzcool.com,Boulder
```

## 4. Run the Tool

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate

# Run in parallel mode
python main.py

# OR run in sequential mode (for testing)
python main.py --mode sequential
```

## 5. Monitor Progress

Watch the console output or check logs:

```bash
# View live log
tail -f logs/automation_*.log

# View submissions
cat logs/submissions.csv

# Check statistics
python main.py --stats
```

## Common Commands

```bash
# Run with 5 parallel workers
MAX_WORKERS=5 python main.py

# Run in visible mode (see browser)
HEADLESS=false python main.py --mode sequential

# Retry failed submissions
python main.py --retry-failed

# Reset and start fresh
python main.py --reset-progress

# Show statistics only
python main.py --stats
```

## Tips for First Run

1. **Start small**: Test with 5-10 contacts first
2. **Use sequential mode**: Easier to debug
3. **Run non-headless**: See what's happening
   ```bash
   HEADLESS=false python main.py --mode sequential
   ```
4. **Check logs**: Review `logs/` directory after each run

## Troubleshooting Quick Fixes

### "Module not found"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Browser not found"
```bash
playwright install chromium
```

### "Config error"
Make sure `.env` has YOUR_EMAIL and YOUR_PHONE filled in.

### Forms not found
Some websites may be difficult to parse. Check logs for details.

## Need Help?

See full documentation in `README.md`

---

**Ready to go?** Run: `python main.py`
