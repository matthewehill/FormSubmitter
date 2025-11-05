"""
Configuration settings for the contact form automation tool
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for the form automation tool"""

    # User Information (Required)
    YOUR_NAME = os.getenv('YOUR_NAME', 'Matt')  # Will append random last name
    YOUR_EMAIL = os.getenv('YOUR_EMAIL', '')  # REQUIRED: Set in .env
    YOUR_PHONE = os.getenv('YOUR_PHONE', '')  # REQUIRED: Set in .env

    # Message Template
    MESSAGE_TEMPLATE = os.getenv(
        'MESSAGE_TEMPLATE',
        "Hello, I've been searching all over {city} to see if there's any HVAC company "
        "that can help me with something. Can someone reach out?"
    )

    # 2Captcha API Settings
    CAPTCHA_API_KEY = os.getenv('CAPTCHA_API_KEY', '')  # REQUIRED if sites have captcha

    # CSV File Settings
    CSV_FILE = os.getenv('CSV_FILE', 'contacts.csv')

    # Browser Settings
    HEADLESS = os.getenv('HEADLESS', 'true').lower() == 'true'
    BROWSER_TYPE = 'chromium'  # chromium, firefox, webkit

    # Timing Settings (seconds)
    MIN_DELAY = int(os.getenv('MIN_DELAY', '5'))
    MAX_DELAY = int(os.getenv('MAX_DELAY', '15'))
    PAGE_LOAD_TIMEOUT = int(os.getenv('PAGE_LOAD_TIMEOUT', '30'))
    FORM_SUBMIT_WAIT = int(os.getenv('FORM_SUBMIT_WAIT', '3'))

    # Parallel Processing
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', '3'))  # Number of parallel browser instances

    # Proxy Settings
    USE_PROXIES = os.getenv('USE_PROXIES', 'false').lower() == 'true'
    PROXY_ROTATION = os.getenv('PROXY_ROTATION', 'false').lower() == 'true'

    # Anti-Detection & Fingerprinting Evasion
    RANDOMIZE_VIEWPORT = os.getenv('RANDOMIZE_VIEWPORT', 'true').lower() == 'true'
    RANDOMIZE_USER_AGENT = os.getenv('RANDOMIZE_USER_AGENT', 'true').lower() == 'true'
    EMULATE_HUMAN_BEHAVIOR = os.getenv('EMULATE_HUMAN_BEHAVIOR', 'true').lower() == 'true'

    # Advanced Stealth
    WEBDRIVER_DETECTION_EVASION = os.getenv('WEBDRIVER_DETECTION_EVASION', 'true').lower() == 'true'
    CANVAS_FINGERPRINT_RANDOMIZATION = os.getenv('CANVAS_FINGERPRINT_RANDOMIZATION', 'false').lower() == 'true'

    # Logging
    LOG_FILE = os.getenv('LOG_FILE', 'automation.log')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Progress Tracking
    PROGRESS_FILE = os.getenv('PROGRESS_FILE', 'progress.json')

    # Form Detection Settings
    MAX_CONTACT_PAGE_SEARCH_DEPTH = 2  # How many links deep to search for contact page
    CONTACT_PAGE_KEYWORDS = [
        'contact', 'get-in-touch', 'reach-out', 'contact-us',
        'get-quote', 'request-quote', 'free-estimate', 'schedule'
    ]

    # Form Field Keywords
    NAME_FIELD_KEYWORDS = ['name', 'full-name', 'fullname', 'your-name', 'firstname', 'first-name']
    EMAIL_FIELD_KEYWORDS = ['email', 'e-mail', 'your-email', 'emailaddress', 'mail']
    PHONE_FIELD_KEYWORDS = ['phone', 'telephone', 'tel', 'mobile', 'contact-number', 'number']
    MESSAGE_FIELD_KEYWORDS = ['message', 'comment', 'comments', 'details', 'description', 'inquiry']

    # User Agents (for rotation)
    USER_AGENTS = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]

    # Default User Agent (if not randomizing)
    USER_AGENT = USER_AGENTS[0]

    # Viewport sizes for randomization
    VIEWPORT_SIZES = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1536, 'height': 864},
        {'width': 1280, 'height': 720},
    ]

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.YOUR_EMAIL:
            errors.append("YOUR_EMAIL is required. Please set it in .env file")
        if not cls.YOUR_PHONE:
            errors.append("YOUR_PHONE is required. Please set it in .env file")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(errors))

        return True
