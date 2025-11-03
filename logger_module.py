"""
Logging configuration for the automation tool
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import Config


def setup_logger(name: str = 'FormAutomation') -> logging.Logger:
    """Setup and configure logger with file and console handlers"""

    logger = logging.getLogger(name)

    # Only setup if not already configured
    if logger.handlers:
        return logger

    # Set log level
    log_level = getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    # Create file handler with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f"{Config.LOG_FILE.replace('.log', '')}_{timestamp}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Logger initialized. Log file: {log_file}")

    return logger


class SubmissionLogger:
    """Specialized logger for tracking form submissions"""

    def __init__(self):
        self.logger = logging.getLogger('FormAutomation.Submissions')
        self.submissions_file = Path('logs') / 'submissions.csv'

        # Create submissions log if it doesn't exist
        if not self.submissions_file.exists():
            with open(self.submissions_file, 'w', encoding='utf-8') as f:
                f.write('timestamp,business_name,website_url,city,status,error_message\n')

    def log_submission(self, business_name: str, website_url: str, city: str,
                      status: str, error_message: str = ''):
        """Log a form submission attempt"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Escape commas and quotes for CSV
        error_message = error_message.replace('"', '""')
        business_name = business_name.replace('"', '""')

        with open(self.submissions_file, 'a', encoding='utf-8') as f:
            f.write(f'{timestamp},"{business_name}",{website_url},{city},{status},"{error_message}"\n')

        # Also log to main logger
        if status == 'SUCCESS':
            self.logger.info(f"✓ {business_name} ({city}) - {website_url}")
        else:
            self.logger.error(f"✗ {business_name} ({city}) - {website_url} - {error_message}")

    def get_stats(self) -> dict:
        """Get submission statistics"""
        stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        if not self.submissions_file.exists():
            return stats

        with open(self.submissions_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[1:]  # Skip header
            stats['total'] = len(lines)

            for line in lines:
                if 'SUCCESS' in line:
                    stats['success'] += 1
                elif 'FAILED' in line:
                    stats['failed'] += 1
                elif 'SKIPPED' in line:
                    stats['skipped'] += 1

        return stats
