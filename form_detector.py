"""
Intelligent form detection module with multiple fallback strategies
"""
import re
from typing import Optional, Dict, List, Tuple
from playwright.async_api import Page, ElementHandle
from config import Config
import logging

logger = logging.getLogger(__name__)


class FormDetector:
    """Detects and analyzes contact forms on web pages"""

    def __init__(self, page: Page):
        self.page = page
        self.config = Config

    async def find_contact_form(self) -> Optional[Dict]:
        """
        Main method to find contact form using multiple strategies
        Returns dict with form info or None if not found
        """
        logger.info(f"Searching for contact form on: {self.page.url}")

        # Strategy 1: Look for forms on current page
        form_data = await self._find_form_on_current_page()
        if form_data:
            logger.info("Found form on current page")
            return form_data

        # Strategy 2: Look for contact page links
        logger.info("No form on current page, searching for contact page...")
        contact_page_url = await self._find_contact_page_link()

        if contact_page_url:
            logger.info(f"Found contact page link: {contact_page_url}")
            try:
                await self.page.goto(contact_page_url, timeout=Config.PAGE_LOAD_TIMEOUT * 1000)
                await self.page.wait_for_load_state('networkidle', timeout=10000)
                form_data = await self._find_form_on_current_page()
                if form_data:
                    logger.info("Found form on contact page")
                    return form_data
            except Exception as e:
                logger.error(f"Error navigating to contact page: {e}")

        # Strategy 3: Look for modal/popup forms
        logger.info("Searching for modal/popup forms...")
        form_data = await self._find_modal_forms()
        if form_data:
            logger.info("Found modal/popup form")
            return form_data

        logger.warning("No contact form found with any strategy")
        return None

    async def _find_form_on_current_page(self) -> Optional[Dict]:
        """Find forms on the current page"""
        try:
            # Wait a bit for any lazy-loaded forms
            await self.page.wait_for_timeout(2000)

            # Get all forms on the page
            forms = await self.page.query_selector_all('form')
            logger.info(f"Found {len(forms)} form(s) on page")

            for i, form in enumerate(forms):
                logger.info(f"Analyzing form {i + 1}/{len(forms)}")
                form_data = await self._analyze_form(form)
                if form_data and self._is_valid_contact_form(form_data):
                    return form_data

            return None
        except Exception as e:
            logger.error(f"Error finding form on current page: {e}")
            return None

    async def _analyze_form(self, form: ElementHandle) -> Optional[Dict]:
        """Analyze a form and extract field information"""
        try:
            form_data = {
                'form_element': form,
                'fields': {},
                'submit_button': None
            }

            # Get all input, textarea, and select elements
            inputs = await form.query_selector_all('input, textarea, select')

            for input_elem in inputs:
                field_info = await self._analyze_field(input_elem)
                if field_info:
                    field_type, field_element = field_info
                    if field_type not in form_data['fields']:
                        form_data['fields'][field_type] = field_element

            # Find submit button
            submit_button = await self._find_submit_button(form)
            form_data['submit_button'] = submit_button

            return form_data
        except Exception as e:
            logger.error(f"Error analyzing form: {e}")
            return None

    async def _analyze_field(self, element: ElementHandle) -> Optional[Tuple[str, ElementHandle]]:
        """Analyze a form field and determine its type"""
        try:
            # Get field attributes
            name = await element.get_attribute('name') or ''
            id_attr = await element.get_attribute('id') or ''
            placeholder = await element.get_attribute('placeholder') or ''
            type_attr = await element.get_attribute('type') or ''
            aria_label = await element.get_attribute('aria-label') or ''

            # Combine all text for analysis
            field_text = f"{name} {id_attr} {placeholder} {aria_label}".lower()

            # Skip hidden fields, submit buttons, and captcha fields
            if type_attr in ['hidden', 'submit', 'button', 'reset']:
                return None
            if 'captcha' in field_text or 'recaptcha' in field_text:
                return None

            # Check for name field
            if any(keyword in field_text for keyword in self.config.NAME_FIELD_KEYWORDS):
                if 'last' not in field_text and 'surname' not in field_text:
                    return ('name', element)

            # Check for email field
            if any(keyword in field_text for keyword in self.config.EMAIL_FIELD_KEYWORDS):
                return ('email', element)

            # Check for phone field
            if any(keyword in field_text for keyword in self.config.PHONE_FIELD_KEYWORDS):
                return ('phone', element)

            # Check for message field
            if any(keyword in field_text for keyword in self.config.MESSAGE_FIELD_KEYWORDS):
                tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                if tag_name == 'textarea' or type_attr == 'textarea':
                    return ('message', element)

            return None
        except Exception as e:
            logger.debug(f"Error analyzing field: {e}")
            return None

    def _is_valid_contact_form(self, form_data: Dict) -> bool:
        """Check if form has minimum required fields"""
        fields = form_data.get('fields', {})

        # Must have at least email and message, or email and name
        has_email = 'email' in fields
        has_message = 'message' in fields
        has_name = 'name' in fields

        is_valid = has_email and (has_message or has_name)

        logger.info(f"Form validation: email={has_email}, name={has_name}, message={has_message}, valid={is_valid}")

        return is_valid

    async def _find_submit_button(self, form: ElementHandle) -> Optional[ElementHandle]:
        """Find the submit button for the form"""
        try:
            # Strategy 1: Look for input[type=submit] or button[type=submit]
            submit = await form.query_selector('input[type="submit"], button[type="submit"]')
            if submit:
                return submit

            # Strategy 2: Look for button with submit-related text
            buttons = await form.query_selector_all('button, input[type="button"]')
            for button in buttons:
                text = await button.inner_text() if await button.evaluate('el => el.tagName') == 'BUTTON' else ''
                value = await button.get_attribute('value') or ''
                button_text = f"{text} {value}".lower()

                if any(word in button_text for word in ['submit', 'send', 'contact', 'get quote', 'request']):
                    return button

            # Strategy 3: Just get the first button
            button = await form.query_selector('button')
            if button:
                return button

            return None
        except Exception as e:
            logger.error(f"Error finding submit button: {e}")
            return None

    async def _find_contact_page_link(self) -> Optional[str]:
        """Find link to contact page"""
        try:
            # Get all links on the page
            links = await self.page.query_selector_all('a')

            for link in links:
                href = await link.get_attribute('href')
                text = await link.inner_text()
                aria_label = await link.get_attribute('aria-label') or ''

                if not href:
                    continue

                # Combine text for analysis
                link_text = f"{href} {text} {aria_label}".lower()

                # Check if link matches contact keywords
                if any(keyword in link_text for keyword in self.config.CONTACT_PAGE_KEYWORDS):
                    # Convert relative URL to absolute
                    full_url = await self.page.evaluate(f'new URL("{href}", document.baseURI).href')
                    return full_url

            return None
        except Exception as e:
            logger.error(f"Error finding contact page link: {e}")
            return None

    async def _find_modal_forms(self) -> Optional[Dict]:
        """Look for forms that might be in modals or hidden with multiple strategies"""
        try:
            # Strategy 1: Look for common modal trigger buttons
            modal_triggers = await self.page.query_selector_all(
                '''button, a[href="#"], a[href*="contact"], [data-toggle="modal"],
                   [data-modal], .contact-button, #contact-btn, .get-quote-btn,
                   [aria-label*="contact" i], [aria-label*="quote" i]'''
            )

            for trigger in modal_triggers[:10]:  # Try first 10 potential triggers
                try:
                    # Check if element is visible
                    is_visible = await trigger.is_visible()
                    if not is_visible:
                        continue

                    text = await trigger.inner_text() if await trigger.evaluate('el => el.tagName') == 'BUTTON' else ''
                    aria_label = await trigger.get_attribute('aria-label') or ''
                    href = await trigger.get_attribute('href') or ''

                    combined_text = f"{text} {aria_label} {href}".lower()

                    if any(word in combined_text for word in ['contact', 'get quote', 'reach out', 'inquiry', 'schedule', 'request']):
                        logger.info(f"Clicking potential modal trigger: {text or aria_label or 'button'}")

                        # Click and wait for modal
                        await trigger.click()
                        await self.page.wait_for_timeout(2000)

                        # Check if a form appeared
                        form_data = await self._find_form_on_current_page()
                        if form_data:
                            logger.info("Found form in modal!")
                            return form_data

                        # If not found, try closing modal and continue
                        await self.page.keyboard.press('Escape')
                        await self.page.wait_for_timeout(500)

                except Exception as e:
                    logger.debug(f"Error clicking modal trigger: {e}")
                    continue

            # Strategy 2: Look for forms in hidden/invisible containers
            logger.info("Checking for hidden forms...")
            hidden_forms_found = await self.page.evaluate('''
                () => {
                    const allForms = document.querySelectorAll('form');
                    let found = 0;
                    allForms.forEach(form => {
                        const style = window.getComputedStyle(form);
                        if (style.display === 'none' || style.visibility === 'hidden') {
                            form.style.display = 'block';
                            form.style.visibility = 'visible';
                            found++;
                        }
                    });
                    return found;
                }
            ''')

            if hidden_forms_found > 0:
                logger.info(f"Unhid {hidden_forms_found} hidden form(s), checking again...")
                await self.page.wait_for_timeout(1000)
                form_data = await self._find_form_on_current_page()
                if form_data:
                    return form_data

            return None

        except Exception as e:
            logger.error(f"Error finding modal forms: {e}")
            return None
