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
ADD_BUTTON_SELECTOR = "#add_btn"
ROW2_INPUT_SELECTOR = "#row2 input"

def retry(action, retries=3, delay=2, exceptions=(Exception,), action_desc=""):
    for attempt in range(1, retries + 1):
        try:
            return action()
        except exceptions as e:
            logging.warning(f"Attempt {attempt} failed for '{action_desc}': {e}")
            if attempt == retries:
                logging.error(f"All {retries} attempts failed for '{action_desc}'.")
                raise
            time.sleep(delay)

def main():
    logging.info("Initializing WebDriver for Selenium 4.15.2")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    try:
        # Step 1: Open the page
        logging.info(f"Opening page: {URL}")
        driver.get(URL)

        # Step 2: Click the 'Add' button with retry logic
        def click_add():
            add_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ADD_BUTTON_SELECTOR))
            )
            add_btn.click()
            logging.info("Clicked the 'Add' button.")
        retry(click_add, retries=3, delay=2, exceptions=(TimeoutException, ElementClickInterceptedException), action_desc="Click 'Add' button")

        # Step 3: Wait for Row 2 input field to appear
        def wait_for_row2_input():
            logging.info("Waiting for Row 2 input field to be present and visible (may take ~5 seconds)...")
            input_elem = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, ROW2_INPUT_SELECTOR))
            )
            logging.info("Row 2 input field is now visible.")
            return input_elem
        row2_input = retry(wait_for_row2_input, retries=2, delay=1, exceptions=(TimeoutException, StaleElementReferenceException), action_desc="Wait for Row 2 input field")

        # Validation: Row 2 input field should be displayed
        if row2_input.is_displayed():
            logging.info("TEST PASSED: Row 2 input field is displayed after clicking the 'Add' button.")
        else:
            logging.error("TEST FAILED: Row 2 input field is NOT displayed after clicking the 'Add' button.")
            raise AssertionError("Row 2 input field not displayed.")

    except Exception as e:
        logging.exception(f"Test failed due to exception: {e}")
    finally:
        driver.quit()
        logging.info("WebDriver session closed.")

if __name__ == "__main__":
    main()