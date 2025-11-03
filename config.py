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

    # User Agent
    USER_AGENT = (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/120.0.0.0 Safari/537.36'
    )

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
