import time
from bs4 import BeautifulSoup

from datetime import datetime

from urllib.request import urlopen


def fetch_tax_page_by_locator_number_requests(locator_number, tax_year='2024', debug=False):
    # https://taxpayments.stlouiscountymo.gov/parcel/view/19U430038/2024
    url = 'https://taxpayments.stlouiscountymo.gov/parcel/view/' + locator_number
    url += '/' + tax_year
    print("fetching tax for:", locator_number)
    html = ''
    try:
        # Step 1: Go to the form page
        if debug:
            print("step 1")
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(html[:1000])  # Print first 1000 characters for debugging

    except Exception as e:
        print("Error occurred:", e)

    finally:
        if debug:
            print("tax fetch complete")

    return html


def parse_tax_details_page(html: str) -> dict:
    """Parses the tax HTML and extracts specific data fields."""    
    print('parsing tax details')

    soup = BeautifulSoup(html, "html.parser")

    # Step 1: Get all divs with the target class
    divs = soup.find_all('div', class_='panel-body overflow-auto')
    
    if len(divs) < 2:
        return {}  # Not enough divs

    # Step 2: Select the second div (index 1)
    target_div = divs[1]
    
    # Step 3: Find the table inside this div
    table = target_div.find('table')
    
    if not table or not table.tbody:
        return {}

    # Step 4: Get the first row in table body
    first_row = table.tbody.find('tr')
    if not first_row:
        return {}

    cells = first_row.find_all('td')
    if len(cells) < 2:
        return {}

    return {
        "unpaid_tax_total": cells[1].get_text(strip=True),
    }


def query_and_write(iterator):
    debug = False
    delimiter = '|'
    count = 1
    # input_file_name = 'locator_number_list_part_%d.txt' % iterator
    # output_file_name = 'tax_output_data_part_%d.csv' % iterator
    input_file_name = 'locator_number_list.txt'
    output_file_name = 'tax_output_data.csv'
    with open(input_file_name) as fi, open(output_file_name, 'w') as fo:
        for line in fi:
            # if count > 200:
            #     return
            for attempt in range(3):
                try:
                    locator_number = line.rstrip()
                    print(count, locator_number)

                    tax_results_page = fetch_tax_page_by_locator_number_requests(
                        locator_number,
                        debug=debug
                    )
                    tax_details = parse_tax_details_page(tax_results_page)
                    if debug:
                        print(tax_details)

                    data_row = locator_number
                    data_row += delimiter
                    data_row += tax_details['unpaid_tax_total']
                    data_row += '\n'
                    fo.write(data_row)

                except Exception as e:
                    print("error on attempt", attempt)
                    print(e)
                    # time.sleep(30)
                    continue
                else:
                    break
            count += 1


def main():
    debug = False
    delimiter = '|'
    count = 1
    # for i in range(9, 25):
        # print(i)
    query_and_write(0)


if __name__ == '__main__':
    startTime = datetime.now()
    # a = fetch_tax_page_by_locator_number_requests('20W340155')
    # b = parse_tax_details_page(a)
    # print(b)
    # a = fetch_property_page_by_locator_number('20W340155')
    # b = parse_property_details(a)
    # print(b)
    # c = fetch_tax_page_by_locator_number('20W340155')
    # d = parse_tax_details_page(c)
    # print(d)

    main()
    # fetched 5 records in 132 s
    # property detail fetcher takes 14 s to do the same
    # trying browser reset
    # fetched 5 records in like 10 seconds
    print("finished, halting")
    print(datetime.now() - startTime)
