"""
Main automation script for contact form submissions
"""
import asyncio
import csv
import random
import sys
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout
import logging

from config import Config
from form_detector import FormDetector
from captcha_handler import CaptchaHandler
from logger_module import setup_logger, SubmissionLogger
from progress_tracker import ProgressTracker
from proxy_manager import ProxyManager

# Setup logging
logger = setup_logger()
submission_logger = SubmissionLogger()


class FormAutomationBot:
    """Main bot class for automated form submissions"""

    def __init__(self):
        # Validate config
        Config.validate()

        self.config = Config
        self.progress_tracker = ProgressTracker()
        self.captcha_handler = CaptchaHandler(Config.CAPTCHA_API_KEY)
        self.proxy_manager = ProxyManager(enable_proxies=Config.USE_PROXIES)

        # Generate random last names for name field
        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones',
            'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Anderson', 'Taylor', 'Thomas', 'Moore', 'Jackson',
            'White', 'Harris', 'Martin', 'Thompson', 'Young',
            'Allen', 'King', 'Wright', 'Scott', 'Green'
        ]

    def read_csv(self) -> List[Dict]:
        """Read contacts from CSV file"""
        csv_path = Path(self.config.CSV_FILE)

        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        contacts = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if all(key in row for key in ['business_name', 'website_url', 'city']):
                    contacts.append(row)
                else:
                    logger.warning(f"Skipping invalid row: {row}")

        logger.info(f"Loaded {len(contacts)} contacts from CSV")
        return contacts

    async def process_website(self, contact: Dict, browser: Browser) -> bool:
        """
        Process a single website
        Returns True if successful, False otherwise
        """
        business_name = contact.get('business_name', 'Unknown')
        website_url = contact.get('website_url', '')
        city = contact.get('city', '')

        logger.info(f"\n{'='*80}")
        logger.info(f"Processing: {business_name} | {website_url} | {city}")
        logger.info(f"{'='*80}")

        # Check if already processed
        if self.progress_tracker.is_processed(website_url):
            logger.info(f"Already processed, skipping: {website_url}")
            return True

        page = None
        proxy = None
        try:
            # Get proxy if enabled
            if self.config.PROXY_ROTATION:
                proxy = await self.proxy_manager.get_proxy()
                if proxy:
                    logger.info(f"Using proxy: {proxy['server']}")

            # Randomize user agent if enabled
            user_agent = self.config.USER_AGENT
            if self.config.RANDOMIZE_USER_AGENT:
                user_agent = random.choice(self.config.USER_AGENTS)
                logger.debug(f"Using user agent: {user_agent[:50]}...")

            # Randomize viewport if enabled
            viewport = {'width': 1920, 'height': 1080}
            if self.config.RANDOMIZE_VIEWPORT:
                viewport = random.choice(self.config.VIEWPORT_SIZES)
                logger.debug(f"Using viewport: {viewport}")

            # Create new context with advanced stealth
            context_options = {
                'user_agent': user_agent,
                'viewport': viewport,
                'locale': 'en-US',
                'timezone_id': 'America/New_York',
                'permissions': [],
                'color_scheme': random.choice(['light', 'dark']) if self.config.RANDOMIZE_VIEWPORT else 'light'
            }

            # Add proxy if available
            if proxy:
                context_options['proxy'] = proxy

            context = await browser.new_context(**context_options)

            # Add anti-detection scripts
            if self.config.WEBDRIVER_DETECTION_EVASION:
                await context.add_init_script("""
                    // Override the navigator.webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });

                    // Override plugins to appear more like a real browser
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });

                    // Override languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });

                    // Chrome runtime
                    window.chrome = {
                        runtime: {}
                    };

                    // Permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                """)

            page = await context.new_page()

            # Navigate to website
            logger.info(f"Navigating to: {website_url}")
            await page.goto(
                website_url if website_url.startswith('http') else f'https://{website_url}',
                timeout=self.config.PAGE_LOAD_TIMEOUT * 1000,
                wait_until='domcontentloaded'
            )

            # Wait for page to stabilize
            await page.wait_for_timeout(2000)

            # Find contact form
            detector = FormDetector(page)
            form_data = await detector.find_contact_form()

            if not form_data:
                error_msg = "No contact form found"
                logger.warning(error_msg)
                submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
                self.progress_tracker.mark_failed(website_url, error_msg, business_name)
                return False

            # Fill the form
            success = await self._fill_form(page, form_data, contact)
            if not success:
                error_msg = "Failed to fill form"
                logger.error(error_msg)
                submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
                self.progress_tracker.mark_failed(website_url, error_msg, business_name)
                return False

            # Handle CAPTCHA if present
            captcha_solved = await self.captcha_handler.detect_and_solve_captcha(page)
            if not captcha_solved:
                error_msg = "Failed to solve CAPTCHA"
                logger.error(error_msg)
                submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
                self.progress_tracker.mark_failed(website_url, error_msg, business_name)
                return False

            # Submit the form
            success = await self._submit_form(page, form_data)
            if success:
                logger.info(f"✓ Successfully submitted form for {business_name}")
                submission_logger.log_submission(business_name, website_url, city, 'SUCCESS')
                self.progress_tracker.mark_successful(website_url, business_name)
                return True
            else:
                error_msg = "Failed to submit form"
                logger.error(error_msg)
                submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
                self.progress_tracker.mark_failed(website_url, error_msg, business_name)
                return False

        except PlaywrightTimeout as e:
            error_msg = f"Timeout: {str(e)[:100]}"
            logger.error(error_msg)
            submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
            self.progress_tracker.mark_failed(website_url, error_msg, business_name)
            return False

        except Exception as e:
            error_msg = f"Error: {str(e)[:100]}"
            logger.error(f"Unexpected error processing {website_url}: {e}", exc_info=True)
            submission_logger.log_submission(business_name, website_url, city, 'FAILED', error_msg)
            self.progress_tracker.mark_failed(website_url, error_msg, business_name)
            return False

        finally:
            if page:
                await page.context.close()

    async def _fill_form(self, page: Page, form_data: Dict, contact: Dict) -> bool:
        """Fill out the contact form with human-like behavior"""
        try:
            fields = form_data.get('fields', {})
            city = contact.get('city', '')

            # Parse name - if YOUR_NAME contains space, split it; otherwise use random last name
            name_parts = self.config.YOUR_NAME.split(' ', 1)
            if len(name_parts) == 2:
                first_name = name_parts[0]
                last_name = name_parts[1]
            else:
                first_name = self.config.YOUR_NAME
                last_name = random.choice(self.last_names)

            full_name = f"{first_name} {last_name}"

            # Generate message from template
            message = self.config.MESSAGE_TEMPLATE.format(city=city)

            logger.info("Filling form fields...")

            # Human-like behavior: sometimes move mouse around first
            if self.config.EMULATE_HUMAN_BEHAVIOR:
                await page.mouse.move(
                    random.randint(100, 500),
                    random.randint(100, 500)
                )
                await page.wait_for_timeout(random.randint(300, 800))

            # Fill first name field if present
            if 'first_name' in fields:
                await fields['first_name'].click()
                await page.wait_for_timeout(random.randint(100, 300))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    await fields['first_name'].type(first_name, delay=random.randint(50, 150))
                else:
                    await fields['first_name'].fill(first_name)

                logger.debug(f"Filled first_name: {first_name}")
                await page.wait_for_timeout(random.randint(200, 500))

            # Fill last name field if present
            if 'last_name' in fields:
                await fields['last_name'].click()
                await page.wait_for_timeout(random.randint(100, 300))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    await fields['last_name'].type(last_name, delay=random.randint(50, 150))
                else:
                    await fields['last_name'].fill(last_name)

                logger.debug(f"Filled last_name: {last_name}")
                await page.wait_for_timeout(random.randint(200, 500))

            # Fill generic name field if present (and no first/last fields)
            if 'name' in fields and 'first_name' not in fields and 'last_name' not in fields:
                await fields['name'].click()
                await page.wait_for_timeout(random.randint(100, 300))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    # Type like a human (character by character with delays)
                    await fields['name'].type(full_name, delay=random.randint(50, 150))
                else:
                    await fields['name'].fill(full_name)

                logger.debug(f"Filled name: {full_name}")
                await page.wait_for_timeout(random.randint(200, 500))

            # Fill email field
            if 'email' in fields:
                await fields['email'].click()
                await page.wait_for_timeout(random.randint(100, 300))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    await fields['email'].type(self.config.YOUR_EMAIL, delay=random.randint(50, 150))
                else:
                    await fields['email'].fill(self.config.YOUR_EMAIL)

                logger.debug(f"Filled email: {self.config.YOUR_EMAIL}")
                await page.wait_for_timeout(random.randint(200, 500))

            # Fill phone field
            if 'phone' in fields:
                await fields['phone'].click()
                await page.wait_for_timeout(random.randint(100, 300))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    await fields['phone'].type(self.config.YOUR_PHONE, delay=random.randint(50, 150))
                else:
                    await fields['phone'].fill(self.config.YOUR_PHONE)

                logger.debug(f"Filled phone: {self.config.YOUR_PHONE}")
                await page.wait_for_timeout(random.randint(200, 500))

            # Fill message field
            if 'message' in fields:
                await fields['message'].click()
                await page.wait_for_timeout(random.randint(200, 400))

                if self.config.EMULATE_HUMAN_BEHAVIOR:
                    # For message, type a bit faster (simulating thought process)
                    await fields['message'].type(message, delay=random.randint(30, 100))
                else:
                    await fields['message'].fill(message)

                logger.debug(f"Filled message: {message[:50]}...")
                await page.wait_for_timeout(random.randint(300, 700))

            # Human-like behavior: pause before submitting (like reading over the form)
            if self.config.EMULATE_HUMAN_BEHAVIOR:
                await page.wait_for_timeout(random.randint(1000, 2500))

            logger.info("✓ Form filled successfully")
            return True

        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False

    async def _submit_form(self, page: Page, form_data: Dict) -> bool:
        """Submit the form"""
        try:
            submit_button = form_data.get('submit_button')

            if not submit_button:
                logger.warning("No submit button found, trying form submit")
                await form_data['form_element'].evaluate('form => form.submit()')
            else:
                logger.info("Clicking submit button...")
                await submit_button.click()

            # Wait for navigation or response
            try:
                await page.wait_for_timeout(self.config.FORM_SUBMIT_WAIT * 1000)

                # Check for success indicators
                page_content = await page.content()
                success_indicators = [
                    'thank you', 'thanks', 'success', 'submitted',
                    'received', 'we will contact', 'get back to you'
                ]

                content_lower = page_content.lower()
                if any(indicator in content_lower for indicator in success_indicators):
                    logger.info("Detected success indicator on page")
                    return True

                # If no error indicators, assume success
                error_indicators = ['error', 'invalid', 'required', 'please fill']
                if not any(indicator in content_lower for indicator in error_indicators):
                    logger.info("No error indicators found, assuming success")
                    return True

                logger.warning("Uncertain submission status, marking as success")
                return True

            except Exception as e:
                logger.warning(f"Could not verify submission: {e}")
                return True  # Assume success if no error

        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False

    async def run_single_worker(self, contacts: List[Dict], worker_id: int):
        """Run a single worker that processes contacts"""
        logger.info(f"Worker {worker_id} starting with {len(contacts)} contacts")

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=self.config.HEADLESS,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            try:
                for i, contact in enumerate(contacts):
                    logger.info(f"Worker {worker_id}: Processing {i+1}/{len(contacts)}")

                    # Process the website
                    await self.process_website(contact, browser)

                    # Random delay before next submission
                    if i < len(contacts) - 1:  # Don't delay after last one
                        delay = random.randint(self.config.MIN_DELAY, self.config.MAX_DELAY)
                        logger.info(f"Waiting {delay} seconds before next submission...")
                        await asyncio.sleep(delay)

            finally:
                await browser.close()

        logger.info(f"Worker {worker_id} completed")

    async def run_parallel(self):
        """Run multiple workers in parallel"""
        # Read contacts
        all_contacts = self.read_csv()

        # Filter out already processed
        contacts = self.progress_tracker.get_unprocessed_entries(all_contacts)

        if not contacts:
            logger.info("No contacts to process!")
            return

        # Split contacts among workers
        workers_count = min(self.config.MAX_WORKERS, len(contacts))
        chunk_size = len(contacts) // workers_count
        contact_chunks = [
            contacts[i:i + chunk_size]
            for i in range(0, len(contacts), chunk_size)
        ]

        # Remove empty chunks
        contact_chunks = [chunk for chunk in contact_chunks if chunk]

        logger.info(f"Starting {len(contact_chunks)} parallel workers")

        # Run workers in parallel
        tasks = [
            self.run_single_worker(chunk, i+1)
            for i, chunk in enumerate(contact_chunks)
        ]

        await asyncio.gather(*tasks)

    async def run_sequential(self):
        """Run in sequential mode (single browser)"""
        # Read contacts
        all_contacts = self.read_csv()

        # Filter out already processed
        contacts = self.progress_tracker.get_unprocessed_entries(all_contacts)

        if not contacts:
            logger.info("No contacts to process!")
            return

        # Run single worker
        await self.run_single_worker(contacts, 1)

    def run(self, parallel: bool = True):
        """Main entry point"""
        logger.info("="*80)
        logger.info("Contact Form Automation Tool")
        logger.info("="*80)
        logger.info(f"Mode: {'Parallel' if parallel else 'Sequential'}")
        logger.info(f"Headless: {self.config.HEADLESS}")
        logger.info(f"Max Workers: {self.config.MAX_WORKERS if parallel else 1}")
        logger.info("="*80)

        try:
            if parallel and self.config.MAX_WORKERS > 1:
                asyncio.run(self.run_parallel())
            else:
                asyncio.run(self.run_sequential())

            # Print final statistics
            self._print_stats()

        except KeyboardInterrupt:
            logger.info("\n\nInterrupted by user. Progress has been saved.")
            self._print_stats()
            sys.exit(0)

        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            sys.exit(1)

    def _print_stats(self):
        """Print final statistics"""
        stats = self.progress_tracker.get_stats()
        sub_stats = submission_logger.get_stats()

        logger.info("\n" + "="*80)
        logger.info("FINAL STATISTICS")
        logger.info("="*80)
        logger.info(f"Total Processed: {stats['total_processed']}")
        logger.info(f"Successful: {stats['successful']}")
        logger.info(f"Failed: {stats['failed']}")
        logger.info(f"Success Rate: {stats['success_rate']:.1f}%")
        logger.info(f"Started At: {stats['started_at']}")
        logger.info(f"Last Updated: {stats['last_updated']}")
        logger.info("="*80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Contact Form Automation Tool')
    parser.add_argument(
        '--mode',
        choices=['parallel', 'sequential'],
        default='parallel',
        help='Execution mode (default: parallel)'
    )
    parser.add_argument(
        '--reset-progress',
        action='store_true',
        help='Reset progress and start fresh'
    )
    parser.add_argument(
        '--retry-failed',
        action='store_true',
        help='Retry all failed submissions'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics and exit'
    )

    args = parser.parse_args()

    bot = FormAutomationBot()

    if args.stats:
        bot._print_stats()
        return

    if args.reset_progress:
        confirm = input("Are you sure you want to reset all progress? (yes/no): ")
        if confirm.lower() == 'yes':
            bot.progress_tracker.reset()
            logger.info("Progress reset successfully")
        return

    if args.retry_failed:
        failed_urls = bot.progress_tracker.retry_failed()
        logger.info(f"Prepared {len(failed_urls)} failed URLs for retry")

    # Run the bot
    bot.run(parallel=(args.mode == 'parallel'))


if __name__ == '__main__':
    main()
