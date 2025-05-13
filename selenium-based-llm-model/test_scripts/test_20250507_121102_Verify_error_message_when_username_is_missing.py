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
)
from webdriver_manager.chrome import ChromeDriverManager

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Test configuration
LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
USERNAME_SELECTOR = "#username"
PASSWORD_SELECTOR = "#password"
SUBMIT_SELECTOR = "#submit"
ERROR_SELECTOR = "#error"
EXPECTED_ERROR_TEXT = "Your username is invalid!"
TEST_PASSWORD = "Password123"
RETRY_COUNT = 2
WAIT_TIMEOUT = 10

def wait_for_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def wait_for_element_visible(driver, by, selector, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, selector))
    )

def click_with_retry(driver, by, selector, retries=RETRY_COUNT):
    last_exception = None
    for attempt in range(retries):
        try:
            elem = wait_for_element_visible(driver, by, selector)
            elem.click()
            return
        except (ElementClickInterceptedException, StaleElementReferenceException) as e:
            logging.warning(f"Click attempt {attempt+1} failed: {e}. Retrying...")
            time.sleep(1)
            last_exception = e
    raise last_exception

def run_test():
    # WebDriver initialization (Selenium 4.15.2 best practice)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info("Opening login page: %s", LOGIN_URL)
        driver.get(LOGIN_URL)

        # Wait for the Username and Password fields to be present
        username_field = wait_for_element(driver, By.CSS_SELECTOR, USERNAME_SELECTOR)
        password_field = wait_for_element(driver, By.CSS_SELECTOR, PASSWORD_SELECTOR)
        submit_button = wait_for_element(driver, By.CSS_SELECTOR, SUBMIT_SELECTOR)

        # Step 1: Leave Username empty
        logging.info("Leaving Username field empty.")

        # Step 2: Enter password only
        logging.info("Entering password into Password field.")
        password_field.clear()
        password_field.send_keys(TEST_PASSWORD)

        # Step 3: Click Submit button with retry
        logging.info("Clicking Submit button.")
        click_with_retry(driver, By.CSS_SELECTOR, SUBMIT_SELECTOR)

        # Step 4: Wait for error message to be visible
        logging.info("Waiting for error message to be displayed.")
        error_elem = wait_for_element_visible(driver, By.CSS_SELECTOR, ERROR_SELECTOR)

        # Step 5: Verify error message is displayed
        if not error_elem.is_displayed():
            logging.error("Error message element is not displayed.")
            return

        # Step 6: Verify error message text
        actual_error_text = error_elem.text.strip()
        logging.info("Actual error message text: '%s'", actual_error_text)
        if actual_error_text == EXPECTED_ERROR_TEXT:
            logging.info("Test PASSED: Correct error message is displayed.")
            test_passed = True
        else:
            logging.error(
                "Test FAILED: Error message text mismatch. Expected: '%s', Got: '%s'",
                EXPECTED_ERROR_TEXT, actual_error_text
            )

    except TimeoutException as e:
        logging.error("Timeout waiting for element: %s", e)
    except NoSuchElementException as e:
        logging.error("Element not found: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
    finally:
        driver.quit()
        if test_passed:
            logging.info("TEST RESULT: PASS")
        else:
            logging.info("TEST RESULT: FAIL")

if __name__ == "__main__":
    run_test()