import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    ElementNotInteractableException,
    TimeoutException,
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

def retry_on_exception(exception, tries=3, delay=1.0):
    """
    Decorator to retry a function if a specific exception is raised.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(1, tries + 1):
                try:
                    return func(*args, **kwargs)
                except exception as exc:
                    last_exc = exc
                    logging.warning(f"Attempt {attempt} failed with {exception.__name__}: {exc}")
                    time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

@retry_on_exception(WebDriverException, tries=2, delay=2.0)
def main():
    # WebDriver setup (Selenium 4.15.2 best practice)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)

    url = "https://practicetestautomation.com/practice-test-exceptions/"
    logging.info(f"Opening page: {url}")
    driver.get(url)

    try:
        # Step 1: Click the 'Add' button
        logging.info("Waiting for 'Add' button to be clickable...")
        add_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#add_btn")))
        logging.info("Clicking 'Add' button.")
        add_button.click()

        # Step 2: Attempt to click the invisible 'Save' button (Row 1)
        # The save button for row 1 is present but hidden (display: none)
        logging.info("Locating invisible 'Save' button for Row 1.")
        save_button = driver.find_element(By.CSS_SELECTOR, "#save_btn")

        # Confirm the button is not displayed
        if save_button.is_displayed():
            logging.error("The 'Save' button is visible, test cannot proceed as expected.")
            driver.quit()
            sys.exit(1)
        else:
            logging.info("'Save' button is invisible as expected. Attempting to click it to trigger ElementNotInteractableException.")

        # Step 3: Attempt to click and expect ElementNotInteractableException
        exception_raised = False
        try:
            save_button.click()
        except ElementNotInteractableException as e:
            logging.info("ElementNotInteractableException was thrown as expected when clicking invisible 'Save' button.")
            exception_raised = True
        except Exception as e:
            logging.error(f"Unexpected exception type: {type(e).__name__}: {e}")
            raise

        if not exception_raised:
            logging.error("ElementNotInteractableException was NOT thrown when clicking invisible 'Save' button. Test FAILED.")
            driver.quit()
            sys.exit(2)
        else:
            logging.info("Test PASSED: ElementNotInteractableException correctly thrown for invisible 'Save' button.")

    finally:
        driver.quit()
        logging.info("WebDriver session closed.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Test execution failed: {e}")
        sys.exit(99)