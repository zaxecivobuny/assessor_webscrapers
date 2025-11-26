import time
from bs4 import BeautifulSoup

from datetime import datetime

# from urllib.request import urlopen

import urllib.request 

from urllib import request

class AppURLopener(urllib.request.FancyURLopener):
    version = 'Mozilla/5.0'


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

        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'referer': 'https://example.com',
            # 'cookie': """your cookie value ( you can get that from your web page) """
        }

        req = request.Request(url, headers=headers) 
        page = request.urlopen( req )

        html_bytes = page.read()
        html = html_bytes.decode("utf-8")

        if debug:
            time.sleep(2)
            print("first fetch:")
            print(html[:1000])  # Print first 1000 characters for debugging

    except Exception as e:
        print("Error occurred:", e)
        # print(e.fp.read())

    finally:
        if debug:
            print("tax fetch complete")

    return html


def parse_tax_details_page(html: str) -> dict:
    """Parses the tax HTML and extracts specific data fields."""    
    print('parsing tax details')

    soup = BeautifulSoup(html, "html.parser")

    target_a_inner_html = None

    unpaid_cell = soup.select('#Billing1 > div:nth-child(2) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2)')


    # Find all table rows with payment history
    rows = soup.select("#PaymentHistoryNF > div.panel-body.overflow-auto > table > tbody > tr")

    for i in range(0, len(rows), 2):
        td5 = rows[i].select_one("td:nth-of-type(5)")
        if td5:
            value = td5.get_text(strip=True)
            if value == "$0.00":
                # Now grab the <a> in that same row under td.text-center
                a_tag = rows[i].select_one("td.text-center > a")
                if a_tag:
                    target_a_inner_html = a_tag.decode_contents()
                break  # stop after first match

    return {
        "unpaid_tax_total": unpaid_cell[0].get_text(strip=True),
        "last_year_paid": target_a_inner_html,
    }

def parse_last_tax_year(html: str) -> str:
    # parse tax HTML to extract just the last tax bill

    soup = BeautifulSoup(html, "html.parser")

    billing = soup.select_one("#Billing1")
    print("billing", billing.get_text())

    selector = "#Billing1 > div:nth-child(2) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)"

    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None



def query_and_write(iterator):
    debug = False
    delimiter = '|'
    count = 1
    if iterator == -1:
        input_file_name = 'data/locator_number_list_sample.txt'
        output_file_name = 'data/tax_output_data_rich_sample.csv'
    elif iterator == 0:
        input_file_name = 'data/locator_number_list.txt'
        output_file_name = 'data/tax_output_data_rich.csv'       
    else:
        input_file_name = 'data/locator_number_list_part_%d.txt' % iterator
        output_file_name = 'data/tax_output_data_rich_part_%d.csv' % iterator

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
                    data_row += delimiter
                    data_row += tax_details['last_year_paid']
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
            return


def main():
    debug = False
    delimiter = '|'
    count = 1
    # for i in range(9, 25):
        # print(i)
    # query_and_write(-1)

    locator_number = '11G330915'
    locator_number = '19U410063'
    year = '2024'
    page = fetch_tax_page_by_locator_number_requests(locator_number, year)
    taxes = parse_last_tax_year(page)
    print("got value:", taxes)



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
