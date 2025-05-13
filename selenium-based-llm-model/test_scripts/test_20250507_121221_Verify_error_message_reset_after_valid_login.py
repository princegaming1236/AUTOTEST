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
    handlers=[logging.StreamHandler(sys.stdout)]
)

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
SUCCESS_URL_FRAGMENT = "practicetestautomation.com/logged-in-successfully/"
SELECTORS = {
    "username_field": "#username",
    "password_field": "#password",
    "submit_button": "#submit",
    "error_message": "#error"
}
TEST_DATA = {
    "valid_username": "student",
    "invalid_username": "invaliduser",
    "password": "Password123"
}
MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (StaleElementReferenceException, ElementClickInterceptedException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt} failed for {func.__name__}: {e}")
                last_exception = e
                time.sleep(1)
        logging.error(f"All retries failed for {func.__name__}")
        raise last_exception
    return wrapper

@retry_on_exception
def fill_input(driver, selector, value):
    elem = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    elem.clear()
    elem.send_keys(value)
    logging.info(f"Filled input {selector} with value '{value}'")

@retry_on_exception
def click_element(driver, selector):
    elem = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    elem.click()
    logging.info(f"Clicked element {selector}")

def wait_for_error_message(driver, should_be_visible=True):
    try:
        if should_be_visible:
            elem = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["error_message"]))
            )
            logging.info("Error message is displayed as expected.")
            return elem.text
        else:
            WebDriverWait(driver, WAIT_TIMEOUT).until_not(
                EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["error_message"]))
            )
            logging.info("Error message is not displayed as expected.")
            return None
    except TimeoutException:
        if should_be_visible:
            logging.error("Expected error message was NOT displayed.")
            raise
        else:
            logging.info("Error message is not visible (as expected).")
            return None

def wait_for_url_contains(driver, fragment):
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.url_contains(fragment)
        )
        logging.info(f"URL contains expected fragment: {fragment}")
    except TimeoutException:
        logging.error(f"URL did not contain expected fragment: {fragment}")
        raise

def is_error_message_displayed(driver):
    try:
        elem = driver.find_element(By.CSS_SELECTOR, SELECTORS["error_message"])
        return elem.is_displayed() and elem.text.strip() != ""
    except NoSuchElementException:
        return False

def main():
    # WebDriver setup (Selenium 4.15.2)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = True

    try:
        logging.info("Opening login page...")
        driver.get(LOGIN_URL)

        # Step 1: Enter invalid username and valid password
        fill_input(driver, SELECTORS["username_field"], TEST_DATA["invalid_username"])
        fill_input(driver, SELECTORS["password_field"], TEST_DATA["password"])
        click_element(driver, SELECTORS["submit_button"])

        # Step 2: Verify error message is displayed
        error_text = wait_for_error_message(driver, should_be_visible=True)
        if "invalid" not in error_text.lower():
            logging.error(f"Unexpected error message text: {error_text}")
            test_passed = False

        # Step 3: Enter valid username and valid password
        fill_input(driver, SELECTORS["username_field"], TEST_DATA["valid_username"])
        fill_input(driver, SELECTORS["password_field"], TEST_DATA["password"])
        click_element(driver, SELECTORS["submit_button"])

        # Step 4: Verify URL contains success fragment
        wait_for_url_contains(driver, SUCCESS_URL_FRAGMENT)

        # Step 5: Verify error message is not displayed on success page
        # The error message element should not be present or visible after redirect
        # Wait a short time to ensure page is loaded
        time.sleep(1)
        error_present = False
        try:
            error_present = is_error_message_displayed(driver)
        except Exception as e:
            logging.info("Error message element not found on success page (expected).")
            error_present = False

        if error_present:
            logging.error("Error message is still displayed after successful login!")
            test_passed = False
        else:
            logging.info("Error message is cleared after successful login (as expected).")

        if test_passed:
            logging.info("TEST PASSED: Error message is reset after valid login.")
        else:
            logging.error("TEST FAILED: Error message was not reset as expected.")

    except Exception as e:
        logging.exception(f"TEST FAILED due to exception: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()