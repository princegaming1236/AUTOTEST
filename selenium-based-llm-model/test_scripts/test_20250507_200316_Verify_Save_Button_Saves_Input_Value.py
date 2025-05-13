import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("TestSaveButton")

# --- Test Data ---
TEST_URL = "https://practicetestautomation.com/practice-test-exceptions/"
EDIT_BTN_SELECTOR = (By.CSS_SELECTOR, "#edit_btn")
SAVE_BTN_SELECTOR = (By.CSS_SELECTOR, "#save_btn")
INPUT_FIELD_SELECTOR = (By.CSS_SELECTOR, "#row1 input")
NEW_INPUT_VALUE = "New Favorite Food"
RETRY_COUNT = 2
WAIT_TIMEOUT = 10

def retry_on_exception(max_retries=RETRY_COUNT, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(f"Attempt {attempt} failed: {e}")
                    last_exc = e
                    time.sleep(1)
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exc
        return wrapper
    return decorator

@retry_on_exception(max_retries=RETRY_COUNT, exceptions=(ElementClickInterceptedException, ElementNotInteractableException, StaleElementReferenceException))
def click_element(driver, locator, description, timeout=WAIT_TIMEOUT):
    logger.info(f"Clicking {description} ({locator})")
    element = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(locator)
    )
    element.click()

@retry_on_exception(max_retries=RETRY_COUNT, exceptions=(ElementNotInteractableException, StaleElementReferenceException))
def clear_and_type(driver, locator, value, description, timeout=WAIT_TIMEOUT):
    logger.info(f"Clearing and typing into {description} ({locator})")
    input_elem = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(locator)
    )
    input_elem.clear()
    input_elem.send_keys(value)

def main():
    logger.info("Initializing WebDriver (Selenium 4.15.2)...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logger.info(f"Opening test page: {TEST_URL}")
        driver.get(TEST_URL)

        # Step 1: Click the 'Edit' button for Row 1
        click_element(driver, EDIT_BTN_SELECTOR, "Edit button for Row 1")

        # Step 2: Enter a new value in the input field
        logger.info("Waiting for input field to be enabled and visible...")
        input_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: d.find_element(*INPUT_FIELD_SELECTOR)
        )
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: not input_field.get_attribute("disabled")
        )
        clear_and_type(driver, INPUT_FIELD_SELECTOR, NEW_INPUT_VALUE, "Row 1 input field")

        # Step 3: Click the 'Save' button
        click_element(driver, SAVE_BTN_SELECTOR, "Save button for Row 1")

        # Step 4: Verify the new value is saved and displayed in the input field
        logger.info("Verifying the new value is saved in the input field...")
        def input_value_is_saved(driver):
            elem = driver.find_element(*INPUT_FIELD_SELECTOR)
            return elem.get_attribute("value") == NEW_INPUT_VALUE and elem.get_attribute("disabled") == "true"

        WebDriverWait(driver, WAIT_TIMEOUT).until(input_value_is_saved)
        logger.info("Test PASSED: The new value was saved and displayed in the input field.")
        test_passed = True

    except (TimeoutException, WebDriverException, AssertionError) as e:
        logger.error(f"Test FAILED: {e}")
    finally:
        driver.quit()
        if not test_passed:
            sys.exit(1)

if __name__ == "__main__":
    main()