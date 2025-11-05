"""
CAPTCHA handling using 2captcha API
Enhanced for bulletproof captcha solving with multiple fallbacks
"""
import asyncio
import logging
from typing import Optional, Tuple
from playwright.async_api import Page
import aiohttp
from config import Config
from twocaptcha import TwoCaptcha
from twocaptcha.api import ApiException, NetworkException

logger = logging.getLogger(__name__)


class CaptchaHandler:
    """Handles CAPTCHA solving using 2captcha service with robust error handling"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"

        # Initialize 2captcha client if API key provided
        self.solver = None
        if api_key:
            self.solver = TwoCaptcha(api_key)
            logger.info("2captcha solver initialized")
        else:
            logger.warning("No 2captcha API key - CAPTCHA solving disabled")

    async def solve_recaptcha_v2(self, page: Page, site_key: str) -> Optional[str]:
        """
        Solve reCAPTCHA v2 with robust error handling and retries
        """
        if not self.solver:
            logger.warning("No 2captcha API key provided, skipping captcha")
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                page_url = page.url
                logger.info(f"Solving reCAPTCHA v2 (attempt {attempt + 1}/{max_retries}) for {page_url}")

                # Use synchronous solve in thread pool to make it async-compatible
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.solver.recaptcha(sitekey=site_key, url=page_url)
                )

                if result and result.get('code'):
                    solution = result['code']
                    logger.info(f"✓ Successfully solved reCAPTCHA v2: {solution[:50]}...")
                    return solution
                else:
                    logger.error(f"Invalid response from 2captcha: {result}")

            except ApiException as e:
                logger.error(f"2captcha API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue

            except NetworkException as e:
                logger.error(f"Network error solving CAPTCHA (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(10)
                    continue

            except Exception as e:
                logger.error(f"Unexpected error solving reCAPTCHA (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue

        logger.error("Failed to solve reCAPTCHA v2 after all retries")
        return None

    async def solve_hcaptcha(self, page: Page, site_key: str) -> Optional[str]:
        """
        Solve hCaptcha with robust error handling and retries
        """
        if not self.solver:
            logger.warning("No 2captcha API key provided, skipping hCaptcha")
            return None

        max_retries = 3
        for attempt in range(max_retries):
            try:
                page_url = page.url
                logger.info(f"Solving hCaptcha (attempt {attempt + 1}/{max_retries}) for {page_url}")

                # Use synchronous solve in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.solver.hcaptcha(sitekey=site_key, url=page_url)
                )

                if result and result.get('code'):
                    solution = result['code']
                    logger.info(f"✓ Successfully solved hCaptcha: {solution[:50]}...")
                    return solution
                else:
                    logger.error(f"Invalid response from 2captcha: {result}")

            except ApiException as e:
                logger.error(f"2captcha API error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue

            except NetworkException as e:
                logger.error(f"Network error solving hCaptcha (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(10)
                    continue

            except Exception as e:
                logger.error(f"Unexpected error solving hCaptcha (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5)
                    continue

        logger.error("Failed to solve hCaptcha after all retries")
        return None

    async def _submit_recaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        """Submit reCAPTCHA to 2captcha (legacy method, kept for compatibility)"""
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
        Detect if there's a captcha on the page and solve it with multiple strategies
        Returns True if no captcha or captcha was solved, False if captcha couldn't be solved
        """
        try:
            # Wait a bit for captcha to load
            await page.wait_for_timeout(2000)

            # Check for reCAPTCHA v2
            recaptcha_frame = await page.query_selector('iframe[src*="recaptcha"], iframe[src*="google.com/recaptcha"]')
            if recaptcha_frame:
                logger.info("✓ Detected reCAPTCHA v2")

                # Get site key
                site_key = await self._get_recaptcha_site_key(page)
                if not site_key:
                    logger.error("Could not find reCAPTCHA site key")
                    # Try to proceed anyway - might not be required
                    return True

                # Solve captcha
                solution = await self.solve_recaptcha_v2(page, site_key)
                if not solution:
                    logger.error("Failed to solve reCAPTCHA - form submission may fail")
                    return False

                # Inject solution with multiple methods
                injected = await self._inject_recaptcha_solution(page, solution)
                if injected:
                    logger.info("✓ reCAPTCHA solution injected successfully")
                    await page.wait_for_timeout(1000)  # Wait for callback
                    return True
                else:
                    logger.error("Failed to inject reCAPTCHA solution")
                    return False

            # Check for hCaptcha
            hcaptcha_frame = await page.query_selector('iframe[src*="hcaptcha"], iframe[src*="hcaptcha.com"]')
            if hcaptcha_frame:
                logger.info("✓ Detected hCaptcha")

                # Get site key
                site_key = await self._get_hcaptcha_site_key(page)
                if not site_key:
                    logger.error("Could not find hCaptcha site key")
                    return True

                # Solve captcha
                solution = await self.solve_hcaptcha(page, site_key)
                if not solution:
                    logger.error("Failed to solve hCaptcha - form submission may fail")
                    return False

                # Inject solution
                injected = await self._inject_hcaptcha_solution(page, solution)
                if injected:
                    logger.info("✓ hCaptcha solution injected successfully")
                    await page.wait_for_timeout(1000)
                    return True
                else:
                    logger.error("Failed to inject hCaptcha solution")
                    return False

            # Check for reCAPTCHA v3 (usually invisible)
            recaptcha_v3 = await page.evaluate('''
                () => {
                    const scripts = Array.from(document.querySelectorAll('script'));
                    return scripts.some(s => s.src.includes('recaptcha/releases/') ||
                                            s.innerHTML.includes('grecaptcha'));
                }
            ''')
            if recaptcha_v3:
                logger.info("Detected possible reCAPTCHA v3 (typically invisible)")
                # v3 typically doesn't need solving - it runs in background
                return True

            logger.debug("No captcha detected on page")
            return True  # No captcha is fine

        except Exception as e:
            logger.error(f"Error detecting/solving captcha: {e}", exc_info=True)
            # Don't fail the whole submission just because of captcha detection error
            return True

    async def _inject_recaptcha_solution(self, page: Page, solution: str) -> bool:
        """Inject reCAPTCHA solution with multiple fallback methods"""
        try:
            # Method 1: Direct textarea injection
            injected = await page.evaluate(f'''
                () => {{
                    const textarea = document.getElementById('g-recaptcha-response');
                    if (textarea) {{
                        textarea.innerHTML = "{solution}";
                        textarea.value = "{solution}";
                        return true;
                    }}
                    return false;
                }}
            ''')

            if injected:
                logger.debug("Injected via textarea")
            else:
                # Method 2: Try all textareas with class/name matching
                injected = await page.evaluate(f'''
                    () => {{
                        const textareas = document.querySelectorAll('textarea[name*="recaptcha"], textarea[id*="recaptcha"]');
                        if (textareas.length > 0) {{
                            textareas.forEach(ta => {{
                                ta.innerHTML = "{solution}";
                                ta.value = "{solution}";
                            }});
                            return true;
                        }}
                        return false;
                    }}
                ''')
                if injected:
                    logger.debug("Injected via textarea search")

            # Trigger callback functions
            await page.evaluate('''
                () => {
                    // Try common callback patterns
                    if (typeof window.captchaCallback === 'function') {
                        window.captchaCallback();
                    }
                    if (typeof window.onCaptchaSuccess === 'function') {
                        window.onCaptchaSuccess();
                    }
                    if (typeof window.onRecaptchaSuccess === 'function') {
                        window.onRecaptchaSuccess();
                    }
                    // Trigger change event
                    const textarea = document.getElementById('g-recaptcha-response');
                    if (textarea) {
                        const event = new Event('change', { bubbles: true });
                        textarea.dispatchEvent(event);
                    }
                }
            ''')

            return True

        except Exception as e:
            logger.error(f"Error injecting reCAPTCHA solution: {e}")
            return False

    async def _inject_hcaptcha_solution(self, page: Page, solution: str) -> bool:
        """Inject hCaptcha solution"""
        try:
            # Inject into hCaptcha response field
            injected = await page.evaluate(f'''
                () => {{
                    const textarea = document.querySelector('textarea[name="h-captcha-response"]');
                    if (textarea) {{
                        textarea.innerHTML = "{solution}";
                        textarea.value = "{solution}";
                        const event = new Event('change', {{ bubbles: true }});
                        textarea.dispatchEvent(event);
                        return true;
                    }}
                    return false;
                }}
            ''')

            if not injected:
                # Try alternate selectors
                await page.evaluate(f'''
                    () => {{
                        const textareas = document.querySelectorAll('textarea[name*="captcha"]');
                        textareas.forEach(ta => {{
                            ta.innerHTML = "{solution}";
                            ta.value = "{solution}";
                        }});
                    }}
                ''')

            # Trigger callbacks
            await page.evaluate('''
                () => {
                    if (typeof window.hcaptchaCallback === 'function') {
                        window.hcaptchaCallback();
                    }
                    if (typeof window.onCaptchaSuccess === 'function') {
                        window.onCaptchaSuccess();
                    }
                }
            ''')

            return True

        except Exception as e:
            logger.error(f"Error injecting hCaptcha solution: {e}")
            return False

    async def _get_hcaptcha_site_key(self, page: Page) -> Optional[str]:
        """Extract hCaptcha site key from page"""
        try:
            site_key = await page.evaluate('''
                () => {
                    // Method 1: data-sitekey attribute
                    const elem = document.querySelector('[data-sitekey]');
                    if (elem) return elem.getAttribute('data-sitekey');

                    // Method 2: iframe src
                    const iframe = document.querySelector('iframe[src*="hcaptcha"]');
                    if (iframe) {
                        const match = iframe.src.match(/[?&]sitekey=([^&]+)/);
                        if (match) return match[1];
                    }

                    return null;
                }
            ''')
            return site_key

        except Exception as e:
            logger.error(f"Error getting hCaptcha site key: {e}")
            return None

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
