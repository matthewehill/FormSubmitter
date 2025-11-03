"""
CAPTCHA handling using 2captcha API
"""
import asyncio
import logging
from typing import Optional
from playwright.async_api import Page
import aiohttp
from config import Config

logger = logging.getLogger(__name__)


class CaptchaHandler:
    """Handles CAPTCHA solving using 2captcha service"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"

    async def solve_recaptcha_v2(self, page: Page, site_key: str) -> Optional[str]:
        """
        Solve reCAPTCHA v2
        """
        if not self.api_key:
            logger.warning("No 2captcha API key provided, skipping captcha")
            return None

        try:
            page_url = page.url
            logger.info(f"Solving reCAPTCHA v2 for {page_url}")

            # Submit captcha to 2captcha
            captcha_id = await self._submit_recaptcha(site_key, page_url)
            if not captcha_id:
                return None

            # Wait for solution
            solution = await self._get_solution(captcha_id)
            if solution:
                logger.info("Successfully solved reCAPTCHA")
                return solution
            else:
                logger.error("Failed to get reCAPTCHA solution")
                return None

        except Exception as e:
            logger.error(f"Error solving reCAPTCHA: {e}")
            return None

    async def _submit_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Submit reCAPTCHA to 2captcha"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'key': self.api_key,
                    'method': 'userrecaptcha',
                    'googlekey': site_key,
                    'pageurl': page_url,
                    'json': 1
                }

                async with session.get(f"{self.base_url}/in.php", params=params) as response:
                    result = await response.json()

                    if result.get('status') == 1:
                        captcha_id = result.get('request')
                        logger.info(f"Captcha submitted, ID: {captcha_id}")
                        return captcha_id
                    else:
                        logger.error(f"Error submitting captcha: {result}")
                        return None

        except Exception as e:
            logger.error(f"Error in _submit_recaptcha: {e}")
            return None

    async def _get_solution(self, captcha_id: str, max_attempts: int = 60) -> Optional[str]:
        """
        Poll for captcha solution
        2captcha typically takes 10-30 seconds
        """
        try:
            async with aiohttp.ClientSession() as session:
                for attempt in range(max_attempts):
                    await asyncio.sleep(5)  # Wait 5 seconds between checks

                    params = {
                        'key': self.api_key,
                        'action': 'get',
                        'id': captcha_id,
                        'json': 1
                    }

                    async with session.get(f"{self.base_url}/res.php", params=params) as response:
                        result = await response.json()

                        if result.get('status') == 1:
                            return result.get('request')
                        elif result.get('request') == 'CAPCHA_NOT_READY':
                            logger.debug(f"Captcha not ready, attempt {attempt + 1}/{max_attempts}")
                            continue
                        else:
                            logger.error(f"Error getting solution: {result}")
                            return None

                logger.error("Timeout waiting for captcha solution")
                return None

        except Exception as e:
            logger.error(f"Error in _get_solution: {e}")
            return None

    async def detect_and_solve_captcha(self, page: Page) -> bool:
        """
        Detect if there's a captcha on the page and solve it
        Returns True if captcha was found and solved, False otherwise
        """
        try:
            # Check for reCAPTCHA v2
            recaptcha_frame = await page.query_selector('iframe[src*="recaptcha"]')
            if recaptcha_frame:
                logger.info("Detected reCAPTCHA v2")

                # Get site key
                site_key = await self._get_recaptcha_site_key(page)
                if not site_key:
                    logger.error("Could not find reCAPTCHA site key")
                    return False

                # Solve captcha
                solution = await self.solve_recaptcha_v2(page, site_key)
                if not solution:
                    return False

                # Inject solution
                await page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{solution}";')
                await page.evaluate('if(typeof window.captchaCallback === "function") window.captchaCallback();')

                logger.info("Captcha solution injected")
                return True

            # Check for reCAPTCHA v3 (usually invisible)
            recaptcha_v3 = await page.query_selector('[data-sitekey]')
            if recaptcha_v3:
                logger.info("Detected possible reCAPTCHA v3 (may not need solving)")
                # v3 typically doesn't need user interaction
                return True

            # Check for hCaptcha
            hcaptcha_frame = await page.query_selector('iframe[src*="hcaptcha"]')
            if hcaptcha_frame:
                logger.warning("Detected hCaptcha - 2captcha supports this but implementation needed")
                return False

            logger.debug("No captcha detected")
            return True  # No captcha is fine

        except Exception as e:
            logger.error(f"Error detecting/solving captcha: {e}")
            return False

    async def _get_recaptcha_site_key(self, page: Page) -> Optional[str]:
        """Extract reCAPTCHA site key from page"""
        try:
            # Method 1: Look for data-sitekey attribute
            site_key = await page.evaluate('''
                () => {
                    const elem = document.querySelector('[data-sitekey]');
                    return elem ? elem.getAttribute('data-sitekey') : null;
                }
            ''')
            if site_key:
                return site_key

            # Method 2: Look in iframe src
            site_key = await page.evaluate('''
                () => {
                    const iframe = document.querySelector('iframe[src*="recaptcha"]');
                    if (iframe) {
                        const match = iframe.src.match(/[?&]k=([^&]+)/);
                        return match ? match[1] : null;
                    }
                    return null;
                }
            ''')
            return site_key

        except Exception as e:
            logger.error(f"Error getting reCAPTCHA site key: {e}")
            return None
