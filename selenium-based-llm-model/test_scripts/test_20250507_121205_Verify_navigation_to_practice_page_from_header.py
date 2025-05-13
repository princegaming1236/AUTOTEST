import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
EXPECTED_URL = "https://practicetestautomation.com/practice/"

def find_practice_link(driver, timeout=10):
    """
    Find the 'PRACTICE' link in the header navigation.
    Returns the WebElement if found, else raises TimeoutException.
    """
    wait = WebDriverWait(driver, timeout)
    # The header nav uses <a> with text 'Practice' (case-insensitive)
    # Use XPath for robust selection
    return wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[normalize-space(text())='Practice']")
        )
    )

def click_with_retry(element, retries=3, delay=1):
    """
    Attempts to click the element, retrying if intercepted.
    """
    for attempt in range(1, retries + 1):
        try:
            element.click()
            return
        except ElementClickInterceptedException as e:
            logging.warning(f"Click intercepted (attempt {attempt}/{retries}): {e}")
            time.sleep(delay)
        except WebDriverException as e:
            logging.error(f"WebDriverException during click: {e}")
            raise
    raise Exception("Failed to click the PRACTICE link after retries.")

def wait_for_url(driver, expected_url, timeout=10):
    """
    Waits until the current URL matches the expected URL.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.url_to_be(expected_url))

def main():
    # WebDriver setup for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info("Opening login page: %s", LOGIN_URL)
        driver.get(LOGIN_URL)

        # Wait for the page to load and PRACTICE link to be present
        try:
            logging.info("Locating 'PRACTICE' link in header...")
            practice_link = find_practice_link(driver)
            logging.info("'PRACTICE' link found.")
        except TimeoutException:
            logging.error("Could not find 'PRACTICE' link in header within timeout.")
            return

        # Click the PRACTICE link with retry logic
        try:
            logging.info("Clicking 'PRACTICE' link...")
            click_with_retry(practice_link)
        except Exception as e:
            logging.error(f"Failed to click 'PRACTICE' link: {e}")
            return

        # Wait for navigation to the expected URL
        try:
            logging.info("Waiting for URL to be: %s", EXPECTED_URL)
            wait_for_url(driver, EXPECTED_URL)
            logging.info("Navigation successful. URL is as expected.")
            test_passed = True
        except TimeoutException:
            current_url = driver.current_url
            logging.error(f"Navigation failed. Current URL: {current_url}")
        except Exception as e:
            logging.error(f"Unexpected error during URL validation: {e}")

    finally:
        driver.quit()
        if test_passed:
            logging.info("TEST RESULT: PASS - User is redirected to the practice page.")
        else:
            logging.error("TEST RESULT: FAIL - User is NOT redirected to the practice page.")

if __name__ == "__main__":
    main()