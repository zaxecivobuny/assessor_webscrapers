# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # or just --headless for older Chrome
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager(driver_version="137.0.7151.56").install())
driver = webdriver.Chrome(service=service, options=options)

# Now you can use driver.get(), etc.


# Define your input
# STREET_NUMBER = "2805"
# STREET_NAME = "SHERWOOD"
# STREET_SUFFIX = "DR"  # e.g., "DR" for Drive

def fetch_address_info_from_form_flow(locator_number, debug=False):

    if debug:
        print(street_number)
        print(street_name)
        print(street_suffix)
    try:
        # Step 1: Go to the form page
        if debug:
            print("step 1")
        driver.get("https://revenue.stlouisco.com/RealEstate/SearchInput.aspx")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(driver.page_source[:1000])  # Print first 1000 characters for debugging


        # Step 2: Make sure "Property Address" radio button is selected
        if debug:
            print("step 2")
        prop_addr_radio = driver.find_element(By.ID, "ctl00_MainContent_rbutLocatorNum")
        if not prop_addr_radio.is_selected():
            prop_addr_radio.click()
            time.sleep(1)  # Let it trigger the postback

        # Step 3: Fill in address form
        if debug:
            print("step 3")
        driver.find_element(By.ID, "ctl00_MainContent_tboxLocatorNum").send_keys(locator_number)


        # Step 4: Click the Search button
        if debug:
            print("step 4")
        driver.find_element(By.ID, "ctl00_MainContent_butFind").click()

        # Step 5: Wait for results table
        if debug:
            print("step 5")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ctl00_MainContent_tableData"))
        )

        # Step 6: Check how many rows are in the table body
        if debug:
            print("step 6")
        rows = driver.find_elements(By.CSS_SELECTOR, "#ctl00_MainContent_tableData tbody tr")
        if len(rows) > 1:
            print("ALERT: More than one search result found.")
        elif len(rows) == 0:
            print("No search results found.")
        else:
            # Step 7: Click the address cell to go to parcel page
            if debug:
                print("step 7")
            address_cell = rows[0].find_elements(By.TAG_NAME, "td")[3]
            address_cell.click()

            # Step 8: Wait for detail page to load
            if debug:
                print("step 8")
                print(driver.page_source[:1000])  # Print first 1000 characters for debugging
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ctl00_MainContent_OwnLeg_labOwnerName"))
            )

            print("Successfully navigated to the parcel detail page.")

            # Optionally, extract something here (e.g., owner name)
            owner = driver.find_element(By.ID, "ctl00_MainContent_OwnLeg_labOwnerName").text
            if debug:
                print("Owner:", owner)

    except Exception as e:
        print("Error occurred:", e)

    finally:
        if debug:
            print("fetch complete")
        results_page = driver.page_source
        

    return results_page

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
        "legal_description": get_text("#ctl00_MainContent_OwnLeg_labLegalDesc"),
    }


def main():
    debug = False
    delimiter = '\t'
    locator_number_list = [
        '06J530106'
    ]
    with open('output_data.csv', 'w') as fo:
        for l in locator_number_list:
            print(l)
            results_page = fetch_address_info_from_form_flow(
                l,
                debug
            )
            results_details = parse_property_details(results_page)
            if debug:
                print(results_details)
            data_row = results_details['taxing_address'] 
            data_row += delimiter
            data_row += results_details['owner_name']
            data_row += delimiter
            data_row += results_details['taxing_address']
            data_row += delimiter
            data_row += results_details['care_of_name']
            data_row += delimiter
            data_row += results_details['mailing_address']
            data_row += delimiter
            data_row += results_details['legal_description']
            data_row += delimiter
            data_row += l
            data_row += '\n'
            fo.write(data_row)

if __name__ == '__main__':
    main()

driver.quit()