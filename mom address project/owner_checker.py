from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import time


def get_property_html(house_number: str, street_name: str, street_suffix="DR") -> str:
    """Navigates to the property detail page and returns HTML source."""
    search_address = f"{house_number} {street_name} {street_suffix}"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920x1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://revenue.stlouisco.com/RealEstate/SearchResults.aspx")
        time.sleep(2)
        print(driver.page_source[:1000])  # Print first 1000 characters for debugging
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MainContent_txtStreetAddress"))
        )
        search_box = driver.find_element(By.ID, "MainContent_txtStreetAddress")
        search_box.clear()
        search_box.send_keys(search_address)
        driver.find_element(By.ID, "MainContent_btnSearch").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "MainContent_dlResults"))
        )
        driver.find_element(By.CSS_SELECTOR, "#MainContent_dlResults a").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "divOwnLegData"))
        )
        time.sleep(1)  # Allow JS content to populate

        return driver.page_source

    finally:
        driver.quit()


def parse_property_details(html: str) -> dict:
    """Parses the property HTML and extracts specific data fields."""
    soup = BeautifulSoup(html, "html.parser")

    def get_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None

    return {
        "owner_name": get_text("#ctl00_MainContent_OwnLeg_labOwnerName"),
        "taxing_address": get_text("#ctl00_MainContent_OwnLeg_labTaxAddr"),
        "care_of_name": get_text("#ctl00_MainContent_OwnLeg_labCareOfName"),
        "mailing_address": get_text("#ctl00_MainContent_OwnLeg_labMailAddr"),
    }


def get_property_details(house_number: str, street_name: str, street_suffix="DR") -> dict:
    """Main interface to get property details from address components."""
    html = get_property_html(house_number, street_name, street_suffix)
    return parse_property_details(html)


def main():
    details = get_property_details("2805", "SHERWOOD")
    print(details)


if __name__ == '__main__':
    main()


