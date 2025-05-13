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
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

URL = "https://practicetestautomation.com/practice-test-exceptions/"
EDIT_BUTTON_SELECTOR = "#edit_btn"
INPUT_FIELD_SELECTOR = "#row1 input"

MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException, TimeoutException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt} failed with exception: {e}")
                last_exception = e
                time.sleep(1)
        logging.error(f"All {MAX_RETRIES} attempts failed for {func.__name__}")
        raise last_exception
    return wrapper

@retry_on_exception
def click_edit_button(driver):
    logging.info("Waiting for Edit button to be clickable...")
    edit_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, EDIT_BUTTON_SELECTOR))
    )
    logging.info("Clicking Edit button for Row 1.")
    edit_btn.click()

@retry_on_exception
def verify_input_enabled(driver):
    logging.info("Waiting for Row 1 input field to be present...")
    input_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, INPUT_FIELD_SELECTOR))
    )
    logging.info("Checking if input field is enabled...")
    if input_field.is_enabled():
        logging.info("SUCCESS: Input field is enabled for editing.")
        return True
    else:
        logging.error("FAIL: Input field is NOT enabled after clicking Edit.")
        return False

def main():
    # WebDriver setup for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info(f"Opening page: {URL}")
        driver.get(URL)

        # Step 1: Click the 'Edit' button for Row 1
        click_edit_button(driver)

        # Step 2: Verify the input field is enabled
        if verify_input_enabled(driver):
            logging.info("Test case PASSED: The input field is enabled for editing after clicking Edit.")
            test_passed = True
        else:
            logging.error("Test case FAILED: The input field is not enabled after clicking Edit.")

    except Exception as e:
        logging.exception(f"Test execution failed: {e}")
    finally:
        driver.quit()
        if test_passed:
            logging.info("TEST RESULT: PASS")
            sys.exit(0)
        else:
            logging.error("TEST RESULT: FAIL")
            sys.exit(1)

if __name__ == "__main__":
    main()