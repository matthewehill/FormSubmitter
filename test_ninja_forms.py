"""
Test script to verify Ninja Forms detection
"""
import asyncio
from playwright.async_api import async_playwright
from form_detector import FormDetector
from logger_module import setup_logger

logger = setup_logger()


async def test_ninja_forms_detection():
    """Test if Ninja Forms can be detected on Feather River Aire website"""
    test_url = "https://www.featherriveraire.com/contact/"

    logger.info("="*80)
    logger.info("Testing Ninja Forms Detection")
    logger.info("="*80)
    logger.info(f"Test URL: {test_url}")
    logger.info("="*80)

    async with async_playwright() as p:
        # Launch browser in non-headless mode so we can see what happens
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )

        try:
            page = await browser.new_page()

            # Navigate to the test URL
            logger.info(f"Navigating to: {test_url}")
            await page.goto(test_url, timeout=30000, wait_until='domcontentloaded')

            # Wait for page to stabilize
            await page.wait_for_timeout(2000)

            # Test form detection
            detector = FormDetector(page)
            form_data = await detector.find_contact_form()

            if form_data:
                logger.info("\n" + "="*80)
                logger.info("✓ SUCCESS! Form detected!")
                logger.info("="*80)

                fields = form_data.get('fields', {})
                logger.info(f"Fields found: {list(fields.keys())}")
                logger.info(f"Has submit button: {form_data.get('submit_button') is not None}")

                logger.info("\nField details:")
                for field_type, element in fields.items():
                    name = await element.get_attribute('name')
                    id_attr = await element.get_attribute('id')
                    logger.info(f"  - {field_type}: name='{name}', id='{id_attr}'")

                logger.info("\n✓ Ninja Forms detection is working correctly!")
            else:
                logger.error("\n" + "="*80)
                logger.error("✗ FAILED! No form detected")
                logger.error("="*80)
                logger.error("Ninja Forms detection did not work as expected")

            # Keep browser open for 5 seconds so user can see the page
            logger.info("\nKeeping browser open for 5 seconds for inspection...")
            await page.wait_for_timeout(5000)

        finally:
            await browser.close()


if __name__ == '__main__':
    asyncio.run(test_ninja_forms_detection())
