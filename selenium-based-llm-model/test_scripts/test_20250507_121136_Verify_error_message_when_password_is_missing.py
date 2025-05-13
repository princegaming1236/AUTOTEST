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
USERNAME = "student"
PASSWORD = ""
EXPECTED_ERROR_TEXT = "Your password is invalid!"

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
            except (NoSuchElementException, StaleElementReferenceException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt} failed with exception: {e}")
                last_exception = e
                time.sleep(1)
        logging.error(f"All {MAX_RETRIES} attempts failed for {func.__name__}")
        raise last_exception
    return wrapper

@retry_on_exception
def open_login_page(driver):
    logging.info(f"Opening login page: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["username_field"]))
    )
    logging.info("Login page loaded successfully.")

@retry_on_exception
def enter_username(driver, username):
    logging.info(f"Entering username: {username}")
    username_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["username_field"]))
    )
    username_input.clear()
    username_input.send_keys(username)
    logging.info("Username entered.")

@retry_on_exception
def leave_password_empty(driver):
    logging.info("Ensuring password field is empty.")
    password_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["password_field"]))
    )
    password_input.clear()
    logging.info("Password field left empty.")

@retry_on_exception
def click_submit(driver):
    logging.info("Clicking the Submit button.")
    submit_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["submit_button"]))
    )
    submit_btn.click()
    logging.info("Submit button clicked.")

@retry_on_exception
def verify_error_message_displayed(driver):
    logging.info("Verifying error message is displayed.")
    error_elem = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, SELECTORS["error_message"]))
    )
    # The error message is only visible when it has the 'show' class
    is_displayed = "show" in error_elem.get_attribute("class")
    if not is_displayed:
        # Wait a bit more in case the class is added with a slight delay
        for _ in range(5):
            time.sleep(0.2)
            if "show" in error_elem.get_attribute("class"):
                is_displayed = True
                break
    assert is_displayed, "Error message is not displayed."
    logging.info("Error message is displayed.")
    return error_elem

def verify_error_message_text(error_elem, expected_text):
    actual_text = error_elem.text.strip()
    logging.info(f"Verifying error message text. Expected: '{expected_text}', Actual: '{actual_text}'")
    assert actual_text == expected_text, f"Error message text mismatch. Expected: '{expected_text}', Actual: '{actual_text}'"
    logging.info("Error message text is correct.")

def main():
    # WebDriver initialization (Selenium 4.15.2 best practice)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        open_login_page(driver)
        enter_username(driver, USERNAME)
        leave_password_empty(driver)
        click_submit(driver)
        error_elem = verify_error_message_displayed(driver)
        verify_error_message_text(error_elem, EXPECTED_ERROR_TEXT)
        logging.info("TEST PASSED: Error message for missing password is displayed and correct.")
        test_passed = True
    except AssertionError as ae:
        logging.error(f"TEST FAILED: {ae}")
    except TimeoutException as te:
        logging.error(f"TEST FAILED: Timeout occurred - {te}")
    except Exception as e:
        logging.error(f"TEST FAILED: Unexpected error - {e}")
    finally:
        driver.quit()
        if not test_passed:
            sys.exit(1)

if __name__ == "__main__":
    main()