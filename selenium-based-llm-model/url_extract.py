from datetime import datetime
import time
from urllib.parse import urlparse, urljoin
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging

class URLExtractor:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        
    def extract_urls(self, base_url, max_depth=2):
        """Recursively extract unique internal URLs with BFS up to max_depth"""
        self.logger.info(f"Starting recursive URL extraction from: {base_url}")
        
        try:
            parsed_base = urlparse(base_url)
            base_domain = parsed_base.netloc
            visited = set()
            to_visit = [(base_url, 0)]  # (url, depth)

            while to_visit:
                current_url, depth = to_visit.pop(0)
                
                if current_url in visited or depth > max_depth:
                    continue
                
                try:
                    self.logger.debug(f"Waiting 1 sec. before processing {current_url}")
                    time.sleep(1)
                    self.driver.get(current_url)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'body'))
                    )
                    visited.add(current_url)
                    self.logger.info(f"Processing depth {depth}: {current_url}")

                    # Extract links from current page
                    links = self.driver.find_elements(By.TAG_NAME, 'a')
                    new_urls = set()

                    for link in links:
                        href = link.get_attribute('href')
                        if not href:
                            continue
                            
                        full_url = urljoin(current_url, href)
                        parsed_url = urlparse(full_url)
                        
                        if parsed_url.netloc == base_domain:
                            # Normalize path and handle root URL
                            path = parsed_url.path.rstrip('/') or '/'
                            #clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}".rstrip('/')
                            clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"
                            if clean_url not in visited:
                                new_urls.add(clean_url)

                    # Add discovered URLs to queue
                    for url in new_urls:
                        if url not in [u for u, _ in to_visit]:
                            to_visit.append((url, depth + 1))
                            
                    self.logger.debug(f"Found {len(new_urls)} new URLs at depth {depth}")

                except Exception as e:
                    self.logger.error(f"Failed to process {current_url}: {str(e)}")

            self.logger.info(f"Total unique URLs found: {len(visited)}")

            for url in visited:
                self.logger.debug(f"Found URL: {url}")

            return sorted(visited)
            
        except Exception as e:
            self.logger.error(f"URL extraction failed: {str(e)}")
            return []

if __name__ == "__main__":
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options

    # Setup argument parser
    parser = argparse.ArgumentParser(description="URL Extraction Utility")
    parser.add_argument("--url", required=True, help="Base URL to start extraction from")
    parser.add_argument("--depth", type=int, default=1, help="Maximum recursion depth (default: 1)")
    parser.add_argument("--loglevel", default="INFO", 
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set logging level")

    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"url_extraction_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=args.loglevel,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    # Initialize browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=Service(), options=chrome_options)

    try:
        extractor = URLExtractor(driver)
        urls = extractor.extract_urls(args.url, max_depth=args.depth)
        
        print("\n" + "="*50)
        print(f"Extracted {len(urls)} URLs from {args.url}:")
        for url in urls:
            print(f" - {url}")
        print("="*50)
        
    finally:
        driver.quit()
