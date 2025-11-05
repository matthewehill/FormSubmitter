# Contact Form Security Testing Tool

⚠️ **IMPORTANT**: This tool is designed for **authorized penetration testing** of web form security. Only use with explicit written permission from website owners.

A bulletproof Python-based automation tool for testing contact form security defenses using Playwright. Features advanced stealth capabilities, CAPTCHA bypass, proxy rotation, and fingerprint evasion for comprehensive security assessment.

## Features

### Core Capabilities
- 🎯 **Advanced Form Detection**: Multiple fallback strategies including modal/hidden form detection
- 🤖 **Intelligent Form Filling**: Dynamic field detection with human behavior simulation
- 🔐 **CAPTCHA Bypass**: Support for reCAPTCHA v2/v3 and hCaptcha via 2captcha API
- ⚡ **Parallel Processing**: Run multiple browser instances simultaneously
- 💾 **Progress Tracking**: Automatic save/resume capability with retry logic
- 📊 **Detailed Logging**: Comprehensive logs and penetration test reports

### Advanced Stealth & Evasion
- 🕵️ **Webdriver Detection Evasion**: Removes automation markers
- 🔄 **Proxy Rotation**: Automatic proxy fetching and rotation
- 🎭 **User Agent Randomization**: Rotate through realistic user agents
- 📐 **Viewport Randomization**: Random browser window sizes
- ⌨️ **Human Behavior Emulation**: Realistic typing speeds, mouse movements, and delays
- 🎨 **Fingerprint Randomization**: Advanced canvas and browser fingerprint evasion

### Penetration Testing
- 📈 **Professional Reports**: Generate detailed security assessment reports
- 🔍 **Vulnerability Detection**: Identify missing CAPTCHA, weak validation, etc.
- 🎯 **Success Rate Tracking**: Measure bypass success rates
- 📝 **Client Deliverables**: Export reports in TXT, JSON, or CSV format

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

### 3. Configure Stealth Features (Optional)

For maximum stealth and evasion capabilities, edit `.env`:

```bash
# Proxy Settings
USE_PROXIES=true                        # Enable proxy usage
PROXY_ROTATION=true                     # Rotate through proxies

# Anti-Detection Features
RANDOMIZE_VIEWPORT=true                 # Randomize window size
RANDOMIZE_USER_AGENT=true               # Randomize user agent
EMULATE_HUMAN_BEHAVIOR=true             # Type like a human
WEBDRIVER_DETECTION_EVASION=true        # Hide automation markers
```

### 4. Prepare your CSV file

Create a `contacts.csv` file with target websites:

```csv
business_name,website_url,city
Test Site 1,https://example1.com,Denver
Test Site 2,https://example2.com,Boulder
```

**Required columns:**
- `business_name`: Name of the business (for reporting)
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

## Stealth & Evasion Capabilities

### Webdriver Detection Evasion

The tool automatically:
- Removes `navigator.webdriver` property
- Spoofs plugin presence
- Overrides navigator properties
- Adds Chrome runtime object
- Modifies permission queries

Enable with: `WEBDRIVER_DETECTION_EVASION=true`

### Proxy Rotation

Automatically fetches and rotates through free proxies:
- ProxyScrape API integration
- Automatic proxy validation
- Round-robin or random selection
- Failed proxy detection and removal

Enable with:
```bash
USE_PROXIES=true
PROXY_ROTATION=true
```

**Note**: Free proxies can be unreliable. For production testing, use paid proxy services.

### Human Behavior Emulation

When `EMULATE_HUMAN_BEHAVIOR=true`:
- Realistic typing speeds (50-150ms per character)
- Random mouse movements
- Natural pauses between fields
- Variable delays before submission
- Click timing variance

### Fingerprint Randomization

- **User Agent Rotation**: 10+ realistic user agents
- **Viewport Randomization**: 5 common screen sizes
- **Timezone/Locale**: Randomized per session
- **Color Scheme**: Light/dark mode variation

## Penetration Test Reporting

### Generate Reports

After running tests, generate professional penetration test reports:

```python
from pentest_report import PentestReportGenerator

generator = PentestReportGenerator()

# Generate text report
report_path = generator.generate_report(results, format='txt')

# Generate JSON report
json_path = generator.generate_report(results, format='json')

# Generate CSV report
csv_path = generator.generate_report(results, format='csv')
```

### Report Contents

Reports include:
- **Executive Summary**: Overall statistics and findings
- **Vulnerable Sites**: Detailed analysis of bypassed forms
- **Protected Sites**: Sites with effective defenses
- **Risk Assessment**: HIGH/MEDIUM/LOW risk levels
- **Recommendations**: Specific security improvements
- **Implementation Guidance**: How to fix vulnerabilities

### Sample Report Output

```
================================================================================
FORM SECURITY PENETRATION TEST REPORT
================================================================================

EXECUTIVE SUMMARY
Total Sites Tested: 100
Successful Form Bypasses: 67
Failed Bypass Attempts: 33
Success Rate: 67.0%

⚠️  CRITICAL FINDING:
   67 site(s) are vulnerable to automated form submission.
   These sites lack adequate protection against bot submissions.

VULNERABLE SITES (HIGH PRIORITY)
[1] Example Company
    URL: https://example.com
    Status: ❌ VULNERABLE
    CAPTCHA: ❌ Not implemented
    Risk Level: HIGH

    RECOMMENDATIONS:
       • Implement CAPTCHA (reCAPTCHA v3 or hCaptcha recommended)
       • Add rate limiting to prevent rapid submissions
       • Implement server-side form validation
       • Add honeypot fields to catch bots
================================================================================
```

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
├── main.py                  # Main orchestration script
├── config.py               # Configuration management
├── form_detector.py        # Advanced form detection logic
├── captcha_handler.py      # CAPTCHA bypass (reCAPTCHA v2/v3, hCaptcha)
├── proxy_manager.py        # Proxy rotation and management
├── pentest_report.py       # Penetration test report generator
├── logger_module.py        # Logging and tracking
├── progress_tracker.py     # Progress tracking with resume capability
├── requirements.txt        # Python dependencies
├── .env                    # Your configuration (create this)
├── .env.example           # Example configuration
├── contacts.csv           # Target websites (create this)
├── progress.json          # Auto-generated progress file
├── logs/                  # Auto-generated logs
│   ├── automation_TIMESTAMP.log
│   └── submissions.csv
└── reports/               # Auto-generated pentest reports
    ├── pentest_report_TIMESTAMP.txt
    ├── pentest_report_TIMESTAMP.json
    └── pentest_report_TIMESTAMP.csv
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

## Authorized Use & Legal Compliance

### ⚠️ CRITICAL: Authorization Requirements

This tool is designed for **AUTHORIZED PENETRATION TESTING ONLY**. Unauthorized use may violate:
- Computer Fraud and Abuse Act (CFAA) - US Federal Law
- Computer Misuse Act - UK Law
- Similar laws in other jurisdictions

### ✅ Authorized Use Cases

**ONLY use this tool when you have:**

1. **Written Authorization**
   - Signed penetration testing agreement
   - Statement of Work (SOW) defining scope
   - Authorization letter from website owner
   - Clear start/end dates for testing

2. **Professional Engagements**
   - Hired as security consultant
   - Red team assessment contracts
   - Security audit engagements
   - Bug bounty programs (with proper scope)

3. **Your Own Systems**
   - Testing your own websites
   - Development/staging environments
   - Internal security assessments

### ❌ NEVER Use For

- Unauthorized testing of third-party websites
- Spam or unsolicited contact form submissions
- Malicious attacks or system disruption
- Violating terms of service
- Bypassing security without permission
- Competitive intelligence gathering
- Any illegal activities

### Best Practices for Authorized Testing

1. **Documentation**
   - Keep authorization documents accessible
   - Document all testing activities
   - Generate professional reports for clients
   - Maintain audit trails

2. **Scope Compliance**
   - Stay within authorized scope
   - Respect testing windows
   - Follow rules of engagement
   - Report findings promptly

3. **Client Communication**
   - Provide detailed vulnerability reports
   - Explain security recommendations
   - Help implement fixes
   - Verify remediation

4. **Professional Standards**
   - Follow OWASP guidelines
   - Adhere to ethical hacking principles
   - Maintain client confidentiality
   - Use responsible disclosure practices

### Report Security Vulnerabilities Responsibly

When you find vulnerabilities:
1. **Notify the client immediately**
2. **Provide detailed reproduction steps**
3. **Suggest remediation measures**
4. **Give reasonable time to fix**
5. **Verify fixes were effective**
6. **Maintain confidentiality**

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

### Version 2.0.0 - Bulletproof Edition
- ✨ **NEW: Advanced Stealth Capabilities**
  - Webdriver detection evasion
  - Browser fingerprint randomization
  - User agent and viewport rotation
  - Human behavior emulation

- 🔄 **NEW: Proxy Support**
  - Automatic proxy fetching and rotation
  - Proxy validation and health checking
  - Multiple proxy source integration

- 🔐 **ENHANCED: CAPTCHA Bypass**
  - hCaptcha support added
  - Improved reCAPTCHA v2/v3 handling
  - Multiple injection methods
  - Robust error handling and retries

- 📊 **NEW: Penetration Test Reports**
  - Professional report generation
  - TXT, JSON, and CSV formats
  - Vulnerability assessment
  - Security recommendations

- 🎯 **ENHANCED: Form Detection**
  - Hidden form detection
  - Modal/popup form support
  - Improved field matching
  - Better submit button detection

- 🤖 **NEW: Human Behavior Simulation**
  - Realistic typing speeds
  - Mouse movements
  - Natural delays and pauses
  - Variable timing patterns

- 🛡️ **ENHANCED: Error Handling**
  - Comprehensive retry logic
  - Better exception handling
  - Graceful degradation
  - Detailed error logging

### Version 1.0.0
- Initial release
- Playwright integration
- Parallel processing
- 2captcha integration
- Progress tracking
- Comprehensive logging

---

**Note**: This tool is designed for authorized penetration testing. Always maintain proper documentation of authorization and testing activities.
