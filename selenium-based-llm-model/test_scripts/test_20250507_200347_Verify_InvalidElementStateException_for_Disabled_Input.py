import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    InvalidElementStateException,
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

def main():
    url = "https://practicetestautomation.com/practice-test-exceptions/"
    input_selector = (By.CSS_SELECTOR, "#row1 input")
    max_retries = 2
    driver = None

    # WebDriver initialization (Selenium 4.15.2 best practice)
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        logging.info("WebDriver started successfully.")
    except WebDriverException as e:
        logging.error(f"Failed to start WebDriver: {e}")
        sys.exit(1)

    try:
        # Step 1: Open the page
        logging.info(f"Opening URL: {url}")
        driver.get(url)

        # Step 2: Wait for the disabled input field in Row 1 to be present
        wait = WebDriverWait(driver, 10)
        input_field = wait.until(
            EC.presence_of_element_located(input_selector)
        )
        logging.info("Located Row 1 input field.")

        # Step 3: Attempt to clear the disabled input field and expect InvalidElementStateException
        for attempt in range(1, max_retries + 1):
            try:
                logging.info(f"Attempt {attempt}: Trying to clear the disabled input field.")
                input_field.clear()
                # If no exception, this is a failure for this test case
                logging.error("Expected InvalidElementStateException was NOT thrown when clearing a disabled input field.")
                print("[FAIL] InvalidElementStateException was NOT thrown when clearing a disabled input field.")
                break
            except InvalidElementStateException:
                logging.info("InvalidElementStateException was correctly thrown when trying to clear a disabled input field.")
                print("[PASS] InvalidElementStateException was thrown as expected.")
                break
            except Exception as e:
                logging.warning(f"Unexpected exception occurred: {type(e).__name__}: {e}")
                if attempt == max_retries:
                    logging.error("Max retries reached. Test failed due to unexpected exception.")
                    print(f"[FAIL] Unexpected exception: {type(e).__name__}: {e}")
                else:
                    time.sleep(1)
    finally:
        if driver:
            driver.quit()
            logging.info("WebDriver session closed.")

if __name__ == "__main__":
    main()