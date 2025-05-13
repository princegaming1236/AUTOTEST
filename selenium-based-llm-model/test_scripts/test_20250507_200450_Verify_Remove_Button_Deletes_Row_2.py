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
    StaleElementReferenceException,
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

URL = "https://practicetestautomation.com/practice-test-exceptions/"
SELECTORS = {
    "add_button": (By.CSS_SELECTOR, "#add_btn"),
    "row2": (By.CSS_SELECTOR, "#row2"),
    "remove_button": (By.CSS_SELECTOR, "#row2 #remove_btn"),
}

def wait_for_element(driver, locator, timeout=10, poll_frequency=0.5, disappear=False):
    """
    Wait for element to appear or disappear.
    """
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency)
        if not disappear:
            return wait.until(EC.presence_of_element_located(locator))
        else:
            return wait.until(EC.invisibility_of_element_located(locator))
    except TimeoutException:
        if not disappear:
            logging.error(f"Timeout: Element {locator} not found after {timeout}s")
        else:
            logging.error(f"Timeout: Element {locator} still visible after {timeout}s")
        return None

def click_with_retry(driver, locator, retries=3, delay=1):
    """
    Click an element with retries and logging.
    """
    for attempt in range(1, retries + 1):
        try:
            elem = wait_for_element(driver, locator, timeout=10)
            if elem:
                elem.click()
                logging.info(f"Clicked element {locator}")
                return True
            else:
                logging.warning(f"Element {locator} not found on attempt {attempt}")
        except (ElementClickInterceptedException, StaleElementReferenceException, WebDriverException) as e:
            logging.warning(f"Attempt {attempt}: Error clicking {locator}: {e}")
            time.sleep(delay)
    logging.error(f"Failed to click element {locator} after {retries} attempts")
    return False

def verify_row2_removed(driver, timeout=5):
    """
    Verify that Row 2 is removed (not present or not displayed).
    """
    try:
        wait = WebDriverWait(driver, timeout, poll_frequency=0.5)
        result = wait.until(EC.invisibility_of_element_located(SELECTORS["row2"]))
        if result:
            logging.info("Row 2 is removed (not visible).")
            return True
        else:
            logging.error("Row 2 is still visible after removal.")
            return False
    except TimeoutException:
        logging.error("Timeout waiting for Row 2 to be removed.")
        return False

def main():
    # WebDriver setup (Selenium 4.15.2 recommended pattern)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    test_passed = False

    try:
        logging.info("Opening the test page...")
        driver.get(URL)

        # Step 1: Click the 'Add' button
        logging.info("Clicking the 'Add' button to add Row 2.")
        if not click_with_retry(driver, SELECTORS["add_button"]):
            raise Exception("Could not click 'Add' button.")

        # Step 2: Wait for Row 2 to appear (it takes ~5s)
        logging.info("Waiting for Row 2 to appear...")
        row2_elem = wait_for_element(driver, SELECTORS["row2"], timeout=10)
        if not row2_elem:
            raise Exception("Row 2 did not appear after clicking 'Add'.")

        # Step 3: Click the 'Remove' button for Row 2
        logging.info("Clicking the 'Remove' button for Row 2.")
        if not click_with_retry(driver, SELECTORS["remove_button"]):
            raise Exception("Could not click 'Remove' button for Row 2.")

        # Step 4: Verify Row 2 is removed
        logging.info("Verifying that Row 2 is removed...")
        if verify_row2_removed(driver, timeout=5):
            logging.info("TEST PASSED: Row 2 was successfully removed.")
            test_passed = True
        else:
            logging.error("TEST FAILED: Row 2 was not removed.")

    except Exception as e:
        logging.exception(f"Test encountered an error: {e}")
    finally:
        driver.quit()
        if test_passed:
            logging.info("Test completed successfully.")
        else:
            logging.error("Test failed.")

if __name__ == "__main__":
    main()