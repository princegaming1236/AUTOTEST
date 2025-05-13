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

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

URL = "https://practicetestautomation.com/practice-test-exceptions/"
ADD_BUTTON_SELECTOR = "#add_btn"
ROW2_SELECTOR = "#row2"

MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def retry_on_exception(func):
    def wrapper(*args, **kwargs):
        last_exception = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logging.warning(f"Attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(1)
        logging.error(f"All {MAX_RETRIES} attempts failed.")
        raise last_exception
    return wrapper

@retry_on_exception
def click_add_button(driver):
    logging.info("Waiting for 'Add' button to be clickable...")
    add_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ADD_BUTTON_SELECTOR))
    )
    logging.info("Clicking 'Add' button.")
    add_btn.click()

@retry_on_exception
def wait_for_row2(driver):
    logging.info("Waiting for Row 2 to appear...")
    row2 = WebDriverWait(driver, WAIT_TIMEOUT + 6).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ROW2_SELECTOR))
    )
    logging.info("Row 2 is now visible.")
    return row2

def main():
    # WebDriver setup (Selenium 4.15.2 pattern)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info(f"Opening page: {URL}")
        driver.get(URL)

        click_add_button(driver)
        row2 = wait_for_row2(driver)

        if row2.is_displayed():
            logging.info("Validation PASSED: Row 2 is displayed after clicking 'Add' button.")
            test_passed = True
        else:
            logging.error("Validation FAILED: Row 2 is not displayed after clicking 'Add' button.")

    except (TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException) as e:
        logging.error(f"Test failed due to exception: {e}")
    finally:
        driver.quit()
        if test_passed:
            logging.info("TEST RESULT: PASS")
        else:
            logging.info("TEST RESULT: FAIL")

if __name__ == "__main__":
    main()