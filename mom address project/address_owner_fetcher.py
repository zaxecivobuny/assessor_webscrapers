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

def reset_connection():
    global service
    global driver 
    global options 
    driver = webdriver.Chrome(service=service, options=options)


# Now you can use driver.get(), etc.


# Define your input
# STREET_NUMBER = "2805"
# STREET_NAME = "SHERWOOD"
# STREET_SUFFIX = "DR"  # e.g., "DR" for Drive

def fetch_address_info_from_form_flow(street_number, street_name, street_suffix, debug=False):

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
        prop_addr_radio = driver.find_element(By.ID, "ctl00_MainContent_rbutAddress")
        if not prop_addr_radio.is_selected():
            prop_addr_radio.click()
            time.sleep(1)  # Let it trigger the postback

        # Step 3: Fill in address form
        if debug:
            print("step 3")
        driver.find_element(By.ID, "ctl00_MainContent_tboxAddrNum").send_keys(street_number)
        driver.find_element(By.ID, "ctl00_MainContent_tboxStreet").send_keys(street_name)

        suffix_select = Select(driver.find_element(By.ID, "ctl00_MainContent_ddboxSuffix"))
        suffix_select.select_by_value(street_suffix)

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
    delimiter = '|'
    suffix_dict = {
        'Avenue': 'AVE',
        'Boulevard': 'BLVD',
        'Court': 'CT',
        'Drive': 'DR',
        'Lane': 'LN',
        'Place': 'PL',
        'Road': 'RD',
        'Street': 'ST',
        'Alley': 'ALY',
        'Bend': 'BND',
        'center': 'CTR',
        'Circle': 'CIR',
        'Club': 'CLB',
        'Corners': 'CORS',
        'Courts': 'CTS',
        'Cove': 'CV',
        'Creek': 'CRK',
        'Crossing': 'XING',
        'Estates': 'EST',
        'Expressway': 'EXPY',
        'Fields': 'FLDS',
        'Forest': 'FRST',
        'Gardens': 'GDNS',
        'Glen': 'GLN',
        'Green': 'GRN',
        'Grove': 'GRV',
        'Haven': 'HVN',
        'Heights': 'HTS',
        'Highway': 'HWY',
        'Hill': 'HL',
        'Junction': 'JCT',
        'Knolls': 'KNLS',
        'Mall': 'MALL',
        'Manor': 'MNR',
        'Meadows': 'MDWS',
        'Mountain': 'MTN',
        'Park': 'PARK',
        'Parkway': 'PKWY',
        'Plaza': 'PLZ',
        'Point': 'PT',
        'Ridge': 'RDG',
        'Row': 'ROW',
        'Run': 'RUN',
        'Shore': 'SHR',
        'Spur': 'SPUR',
        'Square': 'SQ',
        'Terrace': 'TER',
        'Trace': 'TRCE',
        'Trail': 'TRL',
        'Valley': 'VLY',
        'View': 'VW',
        'Village': 'VLG',
        'Walk': 'WALK',
        'Way': 'WAY'
    }
    with open('address_list_master_formatted.txt') as fi, open('output_data.csv', 'w') as fo:
        for line in fi:
            for attempt in range(3):
                try:
                    address = line.rstrip()
                    print(address)
                    a = address.split(' ')
                    street_number = a[0]
                    street_name = ' '.join(a[1:-1])
                    street_suffix = suffix_dict[a[-1]]
                    results_page = fetch_address_info_from_form_flow(
                        street_number,
                        street_name,
                        street_suffix,
                        debug
                    )
                    results_details = parse_property_details(results_page)
                    if debug:
                        print(results_details)
                    data_row = address 
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
                    data_row += '\n'
                    fo.write(data_row)
                except Exception as e:
                    print("error on attempt", attempt)
                    reset_connection()
                    # time.sleep(30)
                    continue
                else:
                    break

if __name__ == '__main__':
    main()

driver.quit()