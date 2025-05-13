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
HOME_URL = "https://practicetestautomation.com/"
HOME_LINK_XPATH = "//a[normalize-space(text())='Home']"
MAX_RETRIES = 2
WAIT_TIMEOUT = 10

def find_and_click_home(driver):
    """Find and click the 'HOME' link in the header with retries and logging."""
    last_exception = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Waiting for 'HOME' link to be clickable in header")
            home_link = WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.element_to_be_clickable((By.XPATH, HOME_LINK_XPATH))
            )
            logging.info("Clicking 'HOME' link")
            home_link.click()
            return
        except (TimeoutException, NoSuchElementException, ElementClickInterceptedException, WebDriverException) as e:
            logging.warning(f"Attempt {attempt}: Failed to click 'HOME' link: {e}")
            last_exception = e
            time.sleep(1)
    logging.error("All attempts to click 'HOME' link failed")
    raise last_exception

def verify_home_url(driver):
    """Verify that the current URL is the home page URL."""
    try:
        logging.info("Waiting for URL to be the home page")
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.url_to_be(HOME_URL))
        current_url = driver.current_url
        if current_url == HOME_URL:
            logging.info(f"SUCCESS: Redirected to home page: {current_url}")
            return True
        else:
            logging.error(f"FAIL: URL after clicking HOME is not as expected: {current_url}")
            return False
    except TimeoutException:
        logging.error(f"FAIL: Timed out waiting for URL to be {HOME_URL}. Current URL: {driver.current_url}")
        return False

def main():
    # WebDriver setup (Selenium 4.15.2 pattern)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    test_passed = False

    try:
        logging.info(f"Opening login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)

        find_and_click_home(driver)
        test_passed = verify_home_url(driver)

    except Exception as e:
        logging.exception(f"Test failed due to unexpected error: {e}")
        test_passed = False
    finally:
        driver.quit()
        if test_passed:
            logging.info("TEST RESULT: PASS - User is redirected to the home page")
        else:
            logging.error("TEST RESULT: FAIL - User is NOT redirected to the home page")

if __name__ == "__main__":
    main()