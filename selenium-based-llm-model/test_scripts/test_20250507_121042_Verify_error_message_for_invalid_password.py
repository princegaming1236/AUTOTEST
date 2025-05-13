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

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

LOGIN_URL = "https://practicetestautomation.com/practice-test-login/"
USERNAME = "student"
PASSWORD = "short"
EXPECTED_ERROR_TEXT = "Your password is invalid!"

SELECTORS = {
    "username_field": (By.CSS_SELECTOR, "#username"),
    "password_field": (By.CSS_SELECTOR, "#password"),
    "submit_button": (By.CSS_SELECTOR, "#submit"),
    "error_message": (By.CSS_SELECTOR, "#error"),
}

MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 2):
            try:
                return func(*args, **kwargs)
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, WebDriverException) as e:
                last_exception = e
                logging.warning(f"Attempt {attempt} failed with exception: {e}")
                if attempt <= MAX_RETRIES:
                    time.sleep(1)
                else:
                    logging.error(f"All {MAX_RETRIES + 1} attempts failed.")
                    raise
        raise last_exception
    return wrapper

@retry_on_exception
def open_login_page(driver):
    logging.info(f"Opening login page: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.presence_of_element_located(SELECTORS["username_field"])
    )
    logging.info("Login page loaded successfully.")

@retry_on_exception
def enter_username(driver, username):
    logging.info(f"Entering username: {username}")
    username_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located(SELECTORS["username_field"])
    )
    username_field.clear()
    username_field.send_keys(username)
    logging.info("Username entered.")

@retry_on_exception
def enter_password(driver, password):
    logging.info(f"Entering password: {password}")
    password_field = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located(SELECTORS["password_field"])
    )
    password_field.clear()
    password_field.send_keys(password)
    logging.info("Password entered.")

@retry_on_exception
def click_submit(driver):
    logging.info("Clicking the Submit button.")
    submit_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable(SELECTORS["submit_button"])
    )
    submit_button.click()
    logging.info("Submit button clicked.")

@retry_on_exception
def verify_error_message_displayed(driver):
    logging.info("Verifying error message is displayed.")
    error_elem = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.visibility_of_element_located(SELECTORS["error_message"])
    )
    # The error message is shown by adding a 'show' class, but always present in DOM.
    # Wait until the text is updated and class 'show' is present.
    WebDriverWait(driver, WAIT_TIMEOUT).until(
        lambda d: "show" in error_elem.get_attribute("class")
    )
    logging.info("Error message is displayed.")
    return error_elem

def verify_error_message_text(error_elem, expected_text):
    actual_text = error_elem.text.strip()
    logging.info(f"Verifying error message text. Expected: '{expected_text}', Actual: '{actual_text}'")
    assert actual_text == expected_text, f"Expected error message '{expected_text}', but got '{actual_text}'"
    logging.info("Error message text is correct.")

def main():
    # WebDriver setup as required for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    test_passed = False
    try:
        open_login_page(driver)
        enter_username(driver, USERNAME)
        enter_password(driver, PASSWORD)
        click_submit(driver)
        error_elem = verify_error_message_displayed(driver)
        verify_error_message_text(error_elem, EXPECTED_ERROR_TEXT)
        logging.info("TEST PASSED: Error message for invalid password is displayed and correct.")
        test_passed = True
    except AssertionError as ae:
        logging.error(f"TEST FAILED: {ae}")
    except Exception as e:
        logging.error(f"TEST FAILED due to unexpected error: {e}")
    finally:
        driver.quit()
        if not test_passed:
            sys.exit(1)

if __name__ == "__main__":
    main()