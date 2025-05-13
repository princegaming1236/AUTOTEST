import logging
import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
    selectors = {
        "add_button": "#add_btn",
        "row2_input_field": "#row2 input"
    }

    # WebDriver setup for Selenium 4.15.2
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()

    try:
        logging.info("Opening page: %s", url)
        driver.get(url)

        # Wait for Add button to be present and clickable
        try:
            add_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["add_button"]))
            )
            logging.info("Add button found and clickable.")
        except TimeoutException:
            logging.error("Add button not found or not clickable.")
            driver.quit()
            return

        # Click the Add button
        logging.info("Clicking the Add button.")
        add_btn.click()

        # Attempt to wait for Row 2 input field for only 3 seconds
        logging.info("Waiting up to 3 seconds for Row 2 input field to appear (should timeout).")
        try:
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selectors["row2_input_field"]))
            )
            logging.error("Row 2 input field appeared within 3 seconds (unexpected). Test FAILED.")
        except TimeoutException:
            logging.info("TimeoutException occurred as expected. Row 2 input field did not appear within 3 seconds. Test PASSED.")

    except Exception as e:
        logging.exception("Unexpected error during test execution: %s", e)
    finally:
        logging.info("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    main()