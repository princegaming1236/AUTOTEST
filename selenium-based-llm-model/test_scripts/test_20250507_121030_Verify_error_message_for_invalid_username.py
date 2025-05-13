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

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
USERNAME = "invaliduser"
PASSWORD = "Password123"
EXPECTED_ERROR = "Your username is invalid!"

SELECTORS = {
    "username_field": "#username",
    "password_field": "#password",
    "submit_button": "#submit",
    "error_message": "#error"
}

MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException, TimeoutException) as e:
                logging.warning(f"Attempt {attempt} failed: {e}")
                last_exception = e
                time.sleep(1)
        logging.error(f"All {MAX_RETRIES} attempts failed for {func.__name__}")
        raise last_exception
    return wrapper

@retry_on_exception
def wait_and_send_keys(driver, selector, value, timeout=WAIT_TIMEOUT):
    elem = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )
    elem.clear()
    elem.send_keys(value)
    logging.info(f"Entered value into field '{selector}': {value}")

@retry_on_exception
def wait_and_click(driver, selector, timeout=WAIT_TIMEOUT):
    elem = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )
    elem.click()
    logging.info(f"Clicked element '{selector}'")

@retry_on_exception
def wait_for_error_message(driver, selector, expected_text, timeout=WAIT_TIMEOUT):
    elem = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
    )
    actual_text = elem.text.strip()
    logging.info(f"Error message displayed: '{actual_text}'")
    assert actual_text == expected_text, f"Expected error message '{expected_text}', got '{actual_text}'"
    logging.info("Error message text matches expected.")

def main():
    # WebDriver setup (Selenium 4.15.2)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info("Opening login page...")
        driver.get(LOGIN_URL)

        # Step 1: Enter invalid username
        wait_and_send_keys(driver, SELECTORS["username_field"], USERNAME)

        # Step 2: Enter valid password
        wait_and_send_keys(driver, SELECTORS["password_field"], PASSWORD)

        # Step 3: Click Submit
        wait_and_click(driver, SELECTORS["submit_button"])

        # Step 4: Verify error message is displayed and correct
        wait_for_error_message(driver, SELECTORS["error_message"], EXPECTED_ERROR)

        logging.info("Test PASSED: Error message for invalid username is displayed and correct.")
        test_passed = True

    except AssertionError as ae:
        logging.error(f"Assertion failed: {ae}")
    except WebDriverException as we:
        logging.error(f"WebDriver error: {we}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        driver.quit()
        if not test_passed:
            logging.info("Test FAILED.")
        else:
            logging.info("Test completed successfully.")

if __name__ == "__main__":
    main()