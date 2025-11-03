"""
Progress tracking module for resume capability
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks which websites have been processed for resume capability"""

    def __init__(self, progress_file: str = None):
        self.progress_file = Path(progress_file or Config.PROGRESS_FILE)
        self.processed_urls: Set[str] = set()
        self.failed_urls: Dict[str, str] = {}  # url -> error message
        self.successful_urls: Set[str] = set()
        self.metadata: Dict = {}

        self._load_progress()

    def _load_progress(self):
        """Load progress from file"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                self.processed_urls = set(data.get('processed', []))
                self.failed_urls = data.get('failed', {})
                self.successful_urls = set(data.get('successful', []))
                self.metadata = data.get('metadata', {})

                logger.info(f"Loaded progress: {len(self.processed_urls)} processed, "
                           f"{len(self.successful_urls)} successful, {len(self.failed_urls)} failed")

            except Exception as e:
                logger.error(f"Error loading progress file: {e}")
                self._init_new_progress()
        else:
            self._init_new_progress()

    def _init_new_progress(self):
        """Initialize new progress tracking"""
        self.processed_urls = set()
        self.failed_urls = {}
        self.successful_urls = set()
        self.metadata = {
            'started_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }

    def save_progress(self):
        """Save progress to file"""
        try:
            self.metadata['last_updated'] = datetime.now().isoformat()

            data = {
                'processed': list(self.processed_urls),
                'successful': list(self.successful_urls),
                'failed': self.failed_urls,
                'metadata': self.metadata
            }

            # Write atomically by writing to temp file first
            temp_file = self.progress_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            # Rename temp file to actual file
            temp_file.replace(self.progress_file)

            logger.debug("Progress saved")

        except Exception as e:
            logger.error(f"Error saving progress: {e}")

    def is_processed(self, url: str) -> bool:
        """Check if URL has already been processed"""
        return url in self.processed_urls

    def mark_successful(self, url: str, business_name: str = ''):
        """Mark URL as successfully processed"""
        self.processed_urls.add(url)
        self.successful_urls.add(url)

        # Remove from failed if it was there
        if url in self.failed_urls:
            del self.failed_urls[url]

        self.save_progress()
        logger.info(f"Marked as successful: {url}")

    def mark_failed(self, url: str, error_message: str, business_name: str = ''):
        """Mark URL as failed"""
        self.processed_urls.add(url)
        self.failed_urls[url] = error_message

        # Remove from successful if it was there
        if url in self.successful_urls:
            self.successful_urls.remove(url)

        self.save_progress()
        logger.warning(f"Marked as failed: {url} - {error_message}")

    def get_unprocessed_entries(self, all_entries: List[Dict]) -> List[Dict]:
        """Filter out already processed entries"""
        unprocessed = [
            entry for entry in all_entries
            if entry.get('website_url') not in self.processed_urls
        ]

        logger.info(f"Total entries: {len(all_entries)}, "
                   f"Already processed: {len(all_entries) - len(unprocessed)}, "
                   f"Remaining: {len(unprocessed)}")

        return unprocessed

    def get_stats(self) -> Dict:
        """Get progress statistics"""
        return {
            'total_processed': len(self.processed_urls),
            'successful': len(self.successful_urls),
            'failed': len(self.failed_urls),
            'success_rate': (len(self.successful_urls) / len(self.processed_urls) * 100)
                           if self.processed_urls else 0,
            'started_at': self.metadata.get('started_at', 'N/A'),
            'last_updated': self.metadata.get('last_updated', 'N/A')
        }

    def reset(self):
        """Reset all progress (use with caution!)"""
        logger.warning("Resetting all progress!")
        self._init_new_progress()
        self.save_progress()

    def retry_failed(self) -> List[str]:
        """Get list of failed URLs to retry"""
        failed_list = list(self.failed_urls.keys())

        # Remove from processed and failed so they can be retried
        for url in failed_list:
            self.processed_urls.discard(url)
            del self.failed_urls[url]

        self.save_progress()

        logger.info(f"Prepared {len(failed_list)} failed URLs for retry")
        return failed_list
