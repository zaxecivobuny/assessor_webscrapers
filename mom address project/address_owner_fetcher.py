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

def init_driver(headless=True):
    global service
    global driver 
    global options 
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # modern headless
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def reset_connection():
    global service
    global driver 
    global options 
    driver = webdriver.Chrome(service=service, options=options)


def wait_for(driver, by, value, timeout=15, desc="element"):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except Exception as e:
        raise RuntimeError(f"Timeout waiting for {desc} ({by}={value}): {e}")


def fetch_address_info_from_form_flow(street_number, street_name, street_suffix, debug=False):
    driver = init_driver(headless=True)

    try:
        # Step 1: Go to the form page
        if debug:
            print("Step 1: loading search page")
        driver.get("https://revenue.stlouisco.com/RealEstate/SearchInput.aspx")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(driver.page_source[:1000])

        # Step 2: Make sure "Property Address" radio button is selected
        if debug:
            print("Step 2: selecting property address radio button")
        prop_addr_radio = wait_for(driver, By.ID, "ctl00_MainContent_rbutAddress", desc="Property Address radio")
        if not prop_addr_radio.is_selected():
            prop_addr_radio.click()
            time.sleep(1)

        # Step 3: Fill in address form
        if debug:
            print("Step 3: filling form")
        wait_for(driver, By.ID, "ctl00_MainContent_tboxAddrNum", desc="Street number field").send_keys(street_number)
        driver.find_element(By.ID, "ctl00_MainContent_tboxStreet").send_keys(street_name)

        suffix_select = Select(driver.find_element(By.ID, "ctl00_MainContent_ddboxSuffix"))
        suffix_select.select_by_value(street_suffix)

        # Step 4: Click the Search button
        if debug:
            print("Step 4: clicking search")
        driver.find_element(By.ID, "ctl00_MainContent_butFind").click()

        # Step 5: Wait for results table
        if debug:
            print("Step 5: waiting for results table")
        wait_for(driver, By.ID, "ctl00_MainContent_tableData", desc="Results table")

        # Step 6: Check rows
        rows = driver.find_elements(By.CSS_SELECTOR, "#ctl00_MainContent_tableData tbody tr")
        if len(rows) > 1:
            print("ALERT: More than one search result found.")
        elif len(rows) == 0:
            print("No search results found.")
        else:
            # Step 7: Click address cell
            if debug:
                print("Step 7: clicking result row")
            address_cell = rows[0].find_elements(By.TAG_NAME, "td")[3]
            address_cell.click()

            # Step 8: Wait for detail page
            if debug:
                print("Step 8: waiting for detail page")
            wait_for(driver, By.ID, "ctl00_MainContent_OwnLeg_labOwnerName", desc="Owner name field")

            print("✅ Successfully navigated to the parcel detail page.")
            owner = driver.find_element(By.ID, "ctl00_MainContent_OwnLeg_labOwnerName").text
            if debug:
                print("Owner:", owner)

        results_page = driver.page_source
        return results_page

    except Exception as e:
        print("💥 Error occurred:", e)
        return None

    finally:
        driver.quit()
        if debug:
            print("fetch complete")



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