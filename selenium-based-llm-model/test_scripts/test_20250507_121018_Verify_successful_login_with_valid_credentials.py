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
    ElementNotInteractableException,
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
SUCCESS_URL_PART = "practicetestautomation.com/logged-in-successfully/"
USERNAME = "student"
PASSWORD = "Password123"

SELECTORS = {
    "username_field": (By.CSS_SELECTOR, "#username"),
    "password_field": (By.CSS_SELECTOR, "#password"),
    "submit_button": (By.CSS_SELECTOR, "#submit"),
    "error_message": (By.CSS_SELECTOR, "#error"),
}

SUCCESS_TEXTS = ["Congratulations", "successfully logged in"]
LOGOUT_BUTTON_XPATH = "//button[contains(translate(., 'LOGOUT', 'logout'), 'log out') or contains(., 'Log out') or contains(., 'LOG OUT')] | //a[contains(translate(., 'LOGOUT', 'logout'), 'log out') or contains(., 'Log out') or contains(., 'LOG OUT')]"

MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, WebDriverException) as e:
                logging.warning(f"Attempt {attempt} failed: {e}")
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
    logging.info("Entering password.")
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

def verify_url_contains(driver, expected_part):
    logging.info(f"Verifying URL contains '{expected_part}'")
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.url_contains(expected_part)
        )
        logging.info("URL verification passed.")
    except TimeoutException:
        logging.error(f"URL did not contain '{expected_part}'. Actual URL: {driver.current_url}")
        raise

def verify_success_text_present(driver):
    logging.info("Verifying success text is present on the page.")
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            lambda d: any(text.lower() in d.page_source.lower() for text in SUCCESS_TEXTS)
        )
        logging.info("Success text found on the page.")
    except TimeoutException:
        logging.error("Success text not found on the page.")
        raise

def verify_logout_button_displayed(driver):
    logging.info("Verifying 'Log out' button is displayed.")
    try:
        logout_button = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.visibility_of_element_located((By.XPATH, LOGOUT_BUTTON_XPATH))
        )
        if logout_button.is_displayed():
            logging.info("'Log out' button is displayed.")
        else:
            logging.error("'Log out' button is not displayed.")
            raise AssertionError("'Log out' button is not displayed.")
    except TimeoutException:
        logging.error("'Log out' button was not found on the page.")
        raise

def main():
    # WebDriver setup for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        open_login_page(driver)
        enter_username(driver, USERNAME)
        enter_password(driver, PASSWORD)
        click_submit(driver)
        verify_url_contains(driver, SUCCESS_URL_PART)
        verify_success_text_present(driver)
        verify_logout_button_displayed(driver)
        logging.info("TEST PASSED: Successful login with valid credentials.")
        test_passed = True
    except Exception as e:
        logging.error(f"TEST FAILED: {e}")
    finally:
        driver.quit()
        if not test_passed:
            sys.exit(1)

if __name__ == "__main__":
    main()