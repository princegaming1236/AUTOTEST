import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

HOME_PAGE_URL = "https://practicetestautomation.com/"
EXCEPTIONS_PAGE_URL = "https://practicetestautomation.com/practice-test-exceptions/"
HOME_LINK_XPATH = "//nav[contains(@class, 'menu') or @class='menu']//a[normalize-space(text())='Home']"

def retry_on_exception(max_retries=3, exceptions=(Exception,), delay=1.0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"Attempt {attempt} failed: {e}")
                    if attempt == max_retries:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_on_exception(max_retries=2, exceptions=(WebDriverException, TimeoutException, StaleElementReferenceException), delay=2)
def click_home_link(driver):
    logging.info("Waiting for the 'Home' link to be visible in the navigation menu...")
    home_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, HOME_LINK_XPATH))
    )
    logging.info("Clicking the 'Home' link in the navigation menu.")
    home_link.click()

def verify_home_page_loaded(driver):
    logging.info("Verifying redirection to the home page...")
    try:
        WebDriverWait(driver, 10).until(
            EC.url_to_be(HOME_PAGE_URL)
        )
        # Optionally, verify the page title or a unique element on the home page
        WebDriverWait(driver, 10).until(
            EC.title_contains("Practice Test Automation")
        )
        logging.info("Successfully redirected to the home page.")
        return True
    except TimeoutException:
        logging.error(f"Failed to verify redirection. Current URL: {driver.current_url}")
        return False

def main():
    # Selenium 4.15.2 WebDriver initialization
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info(f"Opening the Exceptions Practice page: {EXCEPTIONS_PAGE_URL}")
        driver.get(EXCEPTIONS_PAGE_URL)

        click_home_link(driver)

        if verify_home_page_loaded(driver):
            logging.info("TEST PASSED: User is redirected to the home page.")
            test_passed = True
        else:
            logging.error("TEST FAILED: User was not redirected to the home page.")

    except Exception as e:
        logging.exception(f"TEST ERROR: {e}")
    finally:
        driver.quit()
        if test_passed:
            logging.info("Test case 'Verify Navigation to Home Page' completed successfully.")
        else:
            logging.error("Test case 'Verify Navigation to Home Page' failed.")

if __name__ == "__main__":
    main()