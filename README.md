# Contact Form Automation Tool

A powerful Python-based automation tool for submitting contact forms at scale using Playwright. Designed for legitimate business outreach with built-in rate limiting, CAPTCHA handling, and progress tracking.

## Features

- 🎯 **Intelligent Form Detection**: Multiple fallback strategies to find contact forms
- 🤖 **Automated Form Filling**: Dynamic field detection and filling
- 🔐 **CAPTCHA Support**: Integration with 2captcha API for solving CAPTCHAs
- ⚡ **Parallel Processing**: Run multiple browser instances simultaneously
- 💾 **Progress Tracking**: Automatic save/resume capability
- 📊 **Detailed Logging**: Comprehensive logs with submission tracking
- 🛡️ **Error Handling**: Robust error handling with retry logic
- ⏱️ **Rate Limiting**: Configurable delays between submissions
- 🎭 **Headless Mode**: Run invisibly for better performance

## System Requirements

- **Operating System**: macOS (also works on Linux/Windows)
- **Python**: 3.8 or higher
- **Browser**: Chrome/Chromium (automatically installed by Playwright)
- **Memory**: 2GB RAM minimum (4GB+ recommended for parallel processing)

## Installation

### 1. Clone or download this repository

```bash
cd /path/to/FormSubmitter
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright browsers

```bash
playwright install chromium
```

This will download the Chromium browser (~300MB).

## Configuration

### 1. Create your .env file

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Edit .env with your details

```bash
# Required Settings
YOUR_NAME=Matt
YOUR_EMAIL=your.email@example.com
YOUR_PHONE=555-123-4567

# Optional: 2Captcha API Key (get from https://2captcha.com)
CAPTCHA_API_KEY=your_2captcha_api_key_here

# CSV File
CSV_FILE=contacts.csv

# Browser Settings
HEADLESS=true

# Timing (seconds)
MIN_DELAY=5
MAX_DELAY=15
PAGE_LOAD_TIMEOUT=30

# Parallel Processing
MAX_WORKERS=3

# Logging
LOG_LEVEL=INFO
```

### 3. Prepare your CSV file

Create a `contacts.csv` file with the following format:

```csv
business_name,website_url,city
ABC Heating & Cooling,https://abchvac.com,Denver
XYZ Air Services,https://xyzair.com,Boulder
```

**Required columns:**
- `business_name`: Name of the business
- `website_url`: Full website URL (include https://)
- `city`: City name (used in message template)

## Usage

### Basic Usage (Parallel Mode)

```bash
python main.py
```

This will:
1. Read contacts from `contacts.csv`
2. Process them in parallel (3 workers by default)
3. Save progress automatically
4. Log all actions to `logs/` directory

### Sequential Mode (One at a time)

```bash
python main.py --mode sequential
```

Use this for:
- Testing
- Debugging
- When parallel processing causes issues

### Command Line Options

```bash
# Run in parallel mode (default)
python main.py --mode parallel

# Run sequentially
python main.py --mode sequential

# Show statistics only
python main.py --stats

# Reset progress and start fresh
python main.py --reset-progress

# Retry all failed submissions
python main.py --retry-failed
```

### Resuming After Interruption

The tool automatically saves progress. Simply run it again:

```bash
python main.py
```

It will skip already processed websites and continue where it left off.

## How It Works

### Form Detection Strategy

The tool uses multiple fallback strategies to find contact forms:

1. **Direct Form Search**: Looks for forms on the current page
2. **Contact Page Navigation**: Finds and navigates to contact/get-quote pages
3. **Modal Detection**: Clicks buttons that open contact modals

### Field Detection

Intelligently detects form fields by analyzing:
- Field names (`name`, `email`, `phone`, `message`)
- IDs (`contact-email`, `your-name`)
- Placeholders (`Enter your email`)
- ARIA labels
- Input types

### Form Filling

The tool fills forms with:
- **Name**: "Matt [RandomLastName]" (uses random last names to avoid spam filters)
- **Email**: Your configured email
- **Phone**: Your configured phone
- **Message**: Template with city variable replaced

Example message:
```
Hello, I've been searching all over Denver to see if there's any HVAC company
that can help me with something. Can someone reach out?
```

### CAPTCHA Handling

When a CAPTCHA is detected:
1. Identifies CAPTCHA type (reCAPTCHA v2, v3, hCaptcha)
2. Sends to 2captcha service
3. Waits for solution (~10-30 seconds)
4. Injects solution into page
5. Continues with submission

**Note**: 2captcha is a paid service. Costs ~$2-3 per 1000 CAPTCHAs.

## File Structure

```
FormSubmitter/
├── main.py                  # Main script
├── config.py               # Configuration management
├── form_detector.py        # Form detection logic
├── captcha_handler.py      # CAPTCHA solving
├── logger_module.py        # Logging setup
├── progress_tracker.py     # Progress tracking
├── requirements.txt        # Python dependencies
├── .env                    # Your configuration (create this)
├── .env.example           # Example configuration
├── contacts.csv           # Your contact list (create this)
├── progress.json          # Auto-generated progress file
└── logs/                  # Auto-generated logs
    ├── automation_TIMESTAMP.log
    └── submissions.csv
```

## Logs and Monitoring

### Log Files

All logs are saved in the `logs/` directory:

- `automation_TIMESTAMP.log`: Detailed execution log
- `submissions.csv`: CSV log of all submissions

### View Logs

```bash
# View latest log
tail -f logs/automation_*.log

# View submissions
cat logs/submissions.csv
```

### Statistics

```bash
python main.py --stats
```

Output:
```
================================================================================
FINAL STATISTICS
================================================================================
Total Processed: 150
Successful: 142
Failed: 8
Success Rate: 94.7%
Started At: 2024-01-15 10:30:00
Last Updated: 2024-01-15 12:45:30
================================================================================
```

## Troubleshooting

### Common Issues

#### 1. "No module named 'playwright'"

```bash
pip install -r requirements.txt
playwright install chromium
```

#### 2. "Configuration errors: YOUR_EMAIL is required"

Make sure you've created `.env` file and filled in required fields.

#### 3. Browser doesn't launch

```bash
# Reinstall browsers
playwright install --force chromium
```

#### 4. "No contact form found" for most sites

Try sequential mode for better debugging:
```bash
python main.py --mode sequential
```

Check logs for specific errors.

#### 5. Too many failures

- Check if websites are blocking automation (some sites detect Playwright)
- Try increasing `PAGE_LOAD_TIMEOUT` in `.env`
- Run in non-headless mode to see what's happening: `HEADLESS=false`

### Debug Mode

Run in non-headless mode to see browser actions:

1. Edit `.env`:
   ```
   HEADLESS=false
   ```

2. Run sequential mode:
   ```bash
   python main.py --mode sequential
   ```

3. Watch the browser to see what's happening

## Performance Tips

### Optimal Settings

For best performance:

```env
MAX_WORKERS=3          # Good balance for most systems
HEADLESS=true          # Better performance
MIN_DELAY=5            # Minimum 5 seconds
MAX_DELAY=15           # Maximum 15 seconds
```

### Resource Usage

- **RAM**: ~300MB per worker
- **CPU**: Moderate (browser rendering)
- **Network**: Depends on sites

### Scaling Up

To process large lists:

1. **More workers**: Increase `MAX_WORKERS=5`
2. **Longer sessions**: Run overnight
3. **Multiple machines**: Split CSV and run on different computers

## Responsible Usage

### ⚠️ Important Guidelines

This tool is designed for **legitimate business outreach** only. Please use responsibly:

✅ **Do:**
- Use for genuine business inquiries
- Respect rate limits
- Provide truthful information
- Honor opt-out requests

❌ **Don't:**
- Send spam or unsolicited advertisements
- Use for malicious purposes
- Overwhelm servers with requests
- Violate website terms of service

### Legal Considerations

- Ensure compliance with CAN-SPAM Act (US) and GDPR (EU)
- Only contact businesses in relevant industries
- Include accurate contact information
- Honor all unsubscribe requests

## Support and Contributing

### Getting Help

If you encounter issues:

1. Check the logs in `logs/` directory
2. Run in debug mode (non-headless, sequential)
3. Review the troubleshooting section

### Customization

You can customize:
- Message templates in `.env`
- Form detection keywords in `config.py`
- Timing and delays in `.env`

## License

This tool is provided as-is for legitimate business purposes. Use responsibly and in compliance with all applicable laws and regulations.

## Changelog

### Version 1.0.0
- Initial release
- Playwright integration
- Parallel processing
- 2captcha integration
- Progress tracking
- Comprehensive logging

---

**Note**: This tool requires active monitoring. Always review logs and adjust settings based on your results.
