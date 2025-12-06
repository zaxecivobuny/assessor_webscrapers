from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import re

# from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

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

    driver.quit()
    driver = webdriver.Chrome(service=service, options=options)


# Define your input
# address

def fetch_property_page_by_address(address, debug=False):
    if debug:
        print("fetching property details for:", address)
    try:
        # Step 1: Go to the form page
        if debug:
            print("step 1")
        driver.get("https://www.stlouis-mo.gov/data/address-search/")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(driver.page_source[:1000])  # Print first 1000 characters for debugging


        # Step 2: Fill in address form
        if debug:
            print("step 2: fill in form")
        driver.find_element(
            By.ID,
            "streetAddress"
        ).send_keys(address)

        # Step 3: Click the Search button
        if debug:
            print("step 3")
        driver.find_element(
            By.CSS_SELECTOR,
            "[name='findByAddress']"
        ).click()

        # Step 4: check if search failed or needs push to results page
        current_url = driver.current_url

        if debug:
            print("step 4: Current URL:", current_url)

        # --- Case 2: Already on parcel detail page
        if "parcelId=" in current_url:
            if debug:
                print("Detected parcel detail page")
        else:

            # --- Case 1 or 3: Same base URL, so check contents
            try:
                # Look for results list
                results = driver.find_elements(By.CSS_SELECTOR, "a.findByAddress")
                if results:
                    if debug:
                        print(f"Detected results list with {len(results)} results, clicking first")
                    results[0].click()
                    # Wait for parcel page to load
                    WebDriverWait(driver, 10).until(
                        EC.url_contains("parcelId=")
                    )
                    if debug:
                        print("arrived at results page")
                        current_url = driver.current_url
                        print("step 4: Current URL:", current_url)


                # If no results, element exists → failed search
                # this is surprisingly tricky as the results page contains the search page
                if driver.find_elements(
                    By.ID,
                    "basic"
                ):
                    # this ID exists on the results page and not on the search page
                    pass
                else:
                    if debug:
                        print("Detected failed search (back to search form)")
                    return "search failed"

            except Exception as e:
                if debug:
                    print("Error detecting page type:", e)

        print("Successfully navigated to the parcel detail page.")

        # Optionally, extract something here (e.g., owner name)
        parcel_id = driver.find_element(By.ID, "asrParcelId").text
        if debug:
            print("Parcel ID:", parcel_id)

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
    def get_td_from_th(th):
        th = soup.find("th", string=lambda t: t and t.strip() == th)
        td = th.find_next_sibling("td").get_text(strip=True)
        return td
    
    # step 1: get total owed from single location

    td = soup.find("td", string=lambda t: t and "Total Amount Due For this Account:" in t)

    if td:
        match = re.search(r"\$[\d,]+\.\d{2}", td.get_text())
        if match:
            amount_due = match.group()
    else:
            amount_due = "Not Found"

    
    # step 2: get oldest tax year owed by iterating list
    
    oldest_tax_year_owed = '2025'

    tax_owed_table = None
    
    for t in soup.find_all("table", class_="data striped"):
        caption = t.find("caption")
        if caption and "Payment history for each of the most recent 3 years" in caption.get_text():
            tax_owed_table = t
            break

    if not tax_owed_table:
        print("Payment history table not found.")
        return {}
    
    for row in tax_owed_table.tbody.find_all("tr"):
        cells = row.find_all("td")

        # Skip rows that don't have enough cells (e.g., summary row)
        if len(cells) < 11:
            continue

        tax_year = cells[0].get_text(strip=True)
        total_balance_text = cells[10].get_text(strip=True)

        # Convert balance string like "$234.73" to float
        try:
            total_balance = float(total_balance_text.replace("$", "").replace(",", ""))
        except ValueError:
            print("error converting total tax balance:", total_balance_text)
            continue

        if total_balance > 0:
            oldest_tax_year_owed = tax_year

    return {
        "parcel_id": get_text("#asrParcelId"),
        "zip_code": get_td_from_th("Zip code"),
        "property_use": get_td_from_th("Property use"),
        "appraised_total": get_td_from_th("Appraised total"),
        "city_taxes_due": amount_due,
        "oldest_unpaid_tax_year": oldest_tax_year_owed
    }


def query_property_and_write(iterator):
    debug = False
    delimiter = '|'
    count = 1
    if iterator == -1:

        input_file_name = 'data/city_address_list_sample.txt'
        output_file_name = 'data/city_locator_output_sample.csv'
    elif iterator == 0:
        input_file_name = 'data/city_address_list_master.txt'
        output_file_name = 'data/city_locator_output_data.csv'
    else:
        input_file_name = 'data/city_address_list_master_part_%d.txt' % iterator
        output_file_name = 'data/city_output_data_part_%d.csv' % iterator

    # input_file_name = 'locator_number_list.txt'
    # output_file_name = 'locator_output_data.csv'
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            # if count > 200:
            #     return
            address = line.rstrip()
            data_row = address
            # print("data_row set", data_row)
            for attempt in range(3):

                try:
                    print(count, address)
                    results_page = fetch_property_page_by_address(
                        address,
                        debug
                    )
                    results_details = parse_property_details(results_page)
                    if debug:
                        print(results_details)

                    data_row = address
                    data_row += delimiter
                    if results_details == {}:
                        data_row += "error accessing"
                    else:
                        data_row += results_details['parcel_id']
                        data_row += delimiter
                        data_row += results_details['zip_code']
                        data_row += delimiter
                        data_row += results_details['property_use']
                        data_row += delimiter
                        data_row += results_details['appraised_total']
                        data_row += delimiter
                        data_row += results_details['city_taxes_due']
                        data_row += delimiter
                        data_row += results_details['oldest_unpaid_tax_year']
                    data_row += '\n'
                    # print("writing rich data row", data_row)
                    fo.write(data_row)
                    data_row = ""
                except Exception as e:
                    print("error on attempt", attempt)
                    print(e)
                    reset_connection()
                    # time.sleep(30)
                    continue
                else:
                    print("reached break")
                    break
            # print('writing data row', data_row)
            fo.write(data_row)
            count += 1




def main():
    # address = '5450 GENEVIEVE AV'
    # address = '5 GENEVIEVE AV'
    # # address = '4213 W MARTIN LUTHER KING DR'
    # m = fetch_property_page_by_address(address, debug=True)
    # # print(m)
    # r = parse_property_details(m)
    # print(r)
    query_property_and_write(1)

if __name__ == '__main__':
    startTime = datetime.now()
    print('starting')
    # a = fetch_property_page_by_locator_number('20W340155')
    # b = parse_property_details(a)
    # print(b)
    # c = fetch_tax_page_by_locator_number('20W340155')
    # d = parse_tax_details_page(c)
    # print(d)

    main()
    print(datetime.now() - startTime)

driver.quit()