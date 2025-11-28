from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup

# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import re


options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # or just --headless for older Chrome
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
# Now you can use driver.get(), etc.

def reset_connection():
    global service
    global driver 
    global options
    print("resetting connection") 
    driver.quit()
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

    def get_text_address(selector):
        el = soup.select_one(selector)
        if el:
            br = el.find('br')

            # Text before the <br>
            addr_line1 = br.previous_sibling.strip() if br and br.previous_sibling else ""

            # Text after the <br>
            addr_line2 = br.next_sibling.strip() if br and br.next_sibling else ""
            # print("a1", addr_line1)
            # print("a2", addr_line2)
            zip_code = addr_line2.split(',')[1][4:]
            # print("zip_code:"+zip_code)
            return [addr_line1, zip_code]

        else:
            return None

    address_list = get_text_address("#ctl00_MainContent_OwnLeg_labTaxAddr")
    if len(address_list) > 1:
        taxing_address_line_1 = address_list[0]
        taxing_address_zip = address_list[1]
    else:
        taxing_address_line_1 = 'unknown'
        taxing_address_zip = 'unknown'

    appraised_total_selector = "#asmt-year-2025 > tbody:nth-child(2) > tr:nth-child(1) > td:nth-child(4)"
    return {
        "owner_name": get_text("#ctl00_MainContent_OwnLeg_labOwnerName"),
        "taxing_address": taxing_address_line_1,
        "taxing_zip": taxing_address_zip,
        "care_of_name": get_text("#ctl00_MainContent_OwnLeg_labCareOfName"),
        "mailing_address": get_text("#ctl00_MainContent_OwnLeg_labMailAddr"),
        "legal_description": get_text("#ctl00_MainContent_OwnLeg_labLegalDesc"),
        "total_acres": get_text("#ctl00_MainContent_OwnLeg_labAcres"),
        "lot_dimensions": get_text("#ctl00_MainContent_OwnLeg_labLotDimensions"),
        "land_use_code": get_text("#ctl00_MainContent_OwnLeg_labLandUseCode"),
        "latest_appraised_total": get_text(appraised_total_selector),
    }


def parse_dimension_string(s):

    if len(s) < 4:
        return 'blank'
    elif 'IRR' in s:
        return 'IRR'
    # case 1, two numbers
    elif re.search(r'^\s*\d{4}\s*/\s*-\s*\d{4}\s*/\s*$', s):
        n = re.findall(r'\d{4}', s)
        return int(n[0]) * int(n[1])
    # case 2, n / n - n
    elif re.search(r'^\s*\d{4}\s*/\s*\d{4}\s*-\s*\d{4}\s*/\s*$', s):
        n = re.findall(r'\d{4}', s)
        return ((int(n[0]) + int(n[1])) / 2) * int(n[2])
    # case 3, n-n/n
    elif re.search(r'^\s*\d{4}\s*/\s*-\s*\d{4}\s*/\s*\d{4}\s*$', s):
        n = re.findall(r'\d{4}', s)
        return int(n[0]) * ((int(n[1]) + int(n[2])) / 2)
    # case 4, n/n-n/n
    elif re.search(r'^\s*\d{4}\s*/\s*\d{4}\s*-\s*\d{4}\s*/\s*\d{4}\s*$', s):
        n = re.findall(r'\d{4}', s)
        return ((int(n[0]) + int(n[1])) / 2) * ((int(n[2]) + int(n[3])) / 2)
    else:
        return 'unknown case'


def query_property_and_write(iterator):
    debug = False
    delimiter = '|'
    count = 1
    if iterator == -1:
        input_file_name = 'data/locator_number_list_sample.txt'
        output_file_name = 'data/locator_output_data_sample.csv'
    if iterator == 0:
        input_file_name = 'data/locator_number_list.txt'
        output_file_name = 'data/locator_output_data.csv'
    else:
        input_file_name = 'data/locator_number_list_part_%d.txt' % iterator
        output_file_name = 'data/locator_output_data_part_%d.csv' % iterator

    # input_file_name = 'locator_number_list.txt'
    # output_file_name = 'locator_output_data.csv'
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            # if count > 200:
            #     return
            locator_number = line.rstrip()
            data_row = locator_number
            for attempt in range(3):
                try:
                    print(count, locator_number)
                    results_page = fetch_property_page_by_locator_number(
                        locator_number,
                        debug
                    )
                    results_details = parse_property_details(results_page)
                    if debug:
                        print(results_details)

                    data_row = locator_number
                    data_row += delimiter
                    data_row += results_details['taxing_address']
                    data_row += delimiter
                    data_row += results_details['taxing_zip']
                    data_row += delimiter
                    data_row += results_details['total_acres']
                    data_row += delimiter
                    data_row += results_details['lot_dimensions']
                    data_row += delimiter
                    data_row += str(
                        parse_dimension_string(results_details['lot_dimensions']))
                    data_row += delimiter
                    data_row += results_details['land_use_code']
                    data_row += delimiter
                    data_row += results_details['latest_appraised_total']
                    # data_row += delimiter
                    # data_row += tax_details['unpaid_tax_total']
                    data_row += '\n'
                    fo.write(data_row)
                    data_row = ""
                except Exception as e:
                    print("error on attempt", attempt)
                    print(e)
                    reset_connection()
                    # time.sleep(30)
                    continue
                else:
                    break
            fo.write(data_row)
            count += 1


def main():
    i = 1
    # for i in range(17, 19):
    #     query_property_and_write(i)
    query_property_and_write(0)

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