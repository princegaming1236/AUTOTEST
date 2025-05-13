import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

URL = "https://practicetestautomation.com/practice-test-exceptions/"
SELECTORS = {
    "instructions_text": "#instructions",
    "add_button": "#add_btn"
}
WAIT_TIMEOUT = 10
RETRY_COUNT = 2

def main():
    # WebDriver setup for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    try:
        logging.info("Opening page: %s", URL)
        driver.get(URL)

        # Step 1: Find the instructions text element
        logging.info("Waiting for instructions text element to be present")
        instructions = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, SELECTORS["instructions_text"]))
        )
        logging.info("Instructions text element found: %s", instructions.text)

        # Step 2: Click the 'Add' button
        logging.info("Waiting for Add button to be clickable")
        add_btn = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTORS["add_button"]))
        )
        logging.info("Clicking the Add button")
        add_btn.click()

        # Step 3: Wait for the instructions element to be removed from DOM
        logging.info("Waiting for instructions text element to be removed from DOM")
        WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.staleness_of(instructions)
        )
        logging.info("Instructions text element has been removed from DOM")

        # Step 4: Attempt to interact with the stale element to trigger StaleElementReferenceException
        stale_exception_raised = False
        for attempt in range(1, RETRY_COUNT + 1):
            try:
                logging.info("Attempt #%d: Accessing instructions text element after removal", attempt)
                # This should raise StaleElementReferenceException
                _ = instructions.text
                logging.warning("No exception raised when accessing stale element (unexpected)")
            except StaleElementReferenceException:
                logging.info("StaleElementReferenceException correctly raised when accessing removed element")
                stale_exception_raised = True
                break
            except Exception as e:
                logging.error("Unexpected exception: %s", e)
                break
            time.sleep(1)

        if stale_exception_raised:
            logging.info("TEST PASSED: StaleElementReferenceException was raised as expected.")
        else:
            logging.error("TEST FAILED: StaleElementReferenceException was NOT raised.")

    except TimeoutException as e:
        logging.error("Timeout waiting for element: %s", e)
    except WebDriverException as e:
        logging.error("WebDriver error: %s", e)
    except Exception as e:
        logging.error("Unexpected error: %s", e)
    finally:
        driver.quit()
        logging.info("Test completed and browser closed.")

if __name__ == "__main__":
    main()