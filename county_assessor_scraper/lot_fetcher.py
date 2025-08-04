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
from datetime import datetime


options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # or just --headless for older Chrome
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager(driver_version="137.0.7151.56").install())
driver = webdriver.Chrome(service=service, options=options)
# Now you can use driver.get(), etc.

def reset_connection():
    global service
    global driver 
    global options 
    driver = webdriver.Chrome(service=service, options=options)




# Define your input
# locator_number

def fetch_property_page_by_locator_number(locator_number, debug=False):
    if debug:
        print("fetching property details for:",locator_number)
    try:
        # Step 1: Go to the form page
        if debug:
            print("step 1")
        driver.get("https://revenue.stlouisco.com/RealEstate/SearchInput.aspx")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(driver.page_source[:1000])  # Print first 1000 characters for debugging


        # Step 2: Make sure "Locator Number" radio button is selected
        if debug:
            print("step 2")
        # prop_addr_radio = driver.find_element(By.ID, "ctl00_MainContent_rbutAddress")
        locator_number_radio = driver.find_element(
            By.ID,
            "ctl00_MainContent_rbutLocatorNum"
        )
        if not locator_number_radio.is_selected():
            locator_number_radio.click()
            time.sleep(1)  # Let it trigger the postback

        # Step 3: Fill in address form
        if debug:
            print("step 3")
        driver.find_element(
            By.ID,
            "ctl00_MainContent_tboxLocatorNum"
        ).send_keys(locator_number)

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
        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "#ctl00_MainContent_tableData tbody tr"
        )
        if len(rows) == 0:
            print("No search results found.")
            return
        elif len(rows) > 1:
            print("ALERT: More than one search result found.")
        else:
            print("exactly one result found")

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
            EC.presence_of_element_located((
                By.ID, "ctl00_MainContent_OwnLeg_labOwnerName"
            ))
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
            print("property fetch complete")
        results_page = driver.page_source
        

    return results_page


def parse_property_details(html: str) -> dict:
    """Parses the property HTML and extracts specific data fields."""
    print('parsing property details')
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
        "total_acres": get_text("#ctl00_MainContent_OwnLeg_labAcres"),
        "lot_dimensions": get_text("#ctl00_MainContent_OwnLeg_labLotDimensions"),
        "land_use_code": get_text("#ctl00_MainContent_OwnLeg_labLandUseCode"),
    }


def main():
    debug = False
    delimiter = '|'
    count = 1
    with open('locator_number_list.txt') as fi, open('parcel_output_data.csv', 'w') as fo:
        for line in fi:
            if count > 200:
                return
            for attempt in range(3):
                try:
                    locator_number = line.rstrip()
                    print(count, locator_number)
                    results_page = fetch_property_page_by_locator_number(
                        locator_number,
                        debug
                    )
                    results_details = parse_property_details(results_page)
                    if debug:
                        print(results_details)
                    
                    # tax_results_page = fetch_tax_page_by_locator_number(
                    #     locator_number,
                    #     debug=debug
                    # )
                    # tax_details = parse_tax_details_page(tax_results_page)
                    # if debug:
                    #     print(tax_details)

                    data_row = locator_number
                    data_row += delimiter
                    data_row += results_details['total_acres']
                    data_row += delimiter
                    data_row += results_details['lot_dimensions']
                    data_row += delimiter
                    data_row += results_details['land_use_code']
                    # data_row += delimiter
                    # data_row += tax_details['unpaid_tax_total']
                    data_row += '\n'
                    fo.write(data_row)
                except Exception as e:
                    print("error on attempt", attempt)
                    print(e)
                    reset_connection()
                    # time.sleep(30)
                    continue
                else:
                    break
            
            count += 1

if __name__ == '__main__':
    startTime = datetime.now()
    # a = fetch_property_page_by_locator_number('20W340155')
    # b = parse_property_details(a)
    # print(b)
    # c = fetch_tax_page_by_locator_number('20W340155')
    # d = parse_tax_details_page(c)
    # print(d)

    main()
    print(datetime.now() - startTime)

driver.quit()