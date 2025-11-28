import time
from bs4 import BeautifulSoup
from datetime import datetime
import urllib.request 
from urllib import request


TAX_YEAR = 2025

def get_parcel_year_amount_owed(locator_number, tax_year='2024', debug=False):
    # https://taxpayments.stlouiscountymo.gov/parcel/view/19U430038/2024
    url = 'https://taxpayments.stlouiscountymo.gov/parcel/view/' + locator_number
    url += '/' + tax_year
    print("fetching tax for:", locator_number, tax_year)
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

    soup = BeautifulSoup(html, "html.parser")
    def get_text(selector):
        el = soup.select_one(selector)
        return el.get_text(strip=True) if el else None


    tax_billed = get_text('#Billing1 > div:nth-child(2) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)')
    amount_owed = get_text('#Billing1 > div:nth-child(2) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(7) > td:nth-child(2)')

    if amount_owed:
        amount_owed_number = money_string_to_float(amount_owed)
    else:
        print("couldn't get taxes", locator_number, tax_year)
        return "couldn't get taxes"
    
    if amount_owed_number > 0:
        return money_string_to_float(tax_billed)
    else:
        return 0

def money_string_to_float(s):
    no_dollar_s = s[1:]
    no_commas_s = no_dollar_s.replace(',','')
    return float(no_commas_s)

def get_total_owed_history(locator_number, year):
    total_owed = 0
    year_int = int(year)
    for i in range(year_int, year_int-12, -1):
        amount = get_parcel_year_amount_owed(locator_number, str(i))
        if amount == 0:
            break
        elif amount == "couldn't get taxes":
            print("error in total")
            return "error: couldn't get taxes " + year 
        else:
            print("adding total")
            total_owed += amount
    return total_owed


def query_and_write(iterator):
    global TAX_YEAR
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
            locator_number = line.rstrip()
            data_row = locator_number
            for attempt in range(1):
                try:
                    locator_number = line.rstrip()
                    print(count, locator_number)

                    tax_amount_owed = get_total_owed_history(
                        locator_number,
                        str(TAX_YEAR)
                    )
                    # print(tax_amount_owed)

                    if type(tax_amount_owed) is str:
                        tax_amount_owed_string = tax_amount_owed
                    else:
                        tax_amount_owed_string = f"{tax_amount_owed:.2f}"

                    if debug:
                        print(tax_amount_owed)

                    data_row = locator_number
                    data_row += delimiter
                    data_row += tax_amount_owed_string
                    data_row += '\n'
                    fo.write(data_row)
                    data_row = ""

                except Exception as e:
                    print("error on attempt", attempt)
                    print(e)
                    # time.sleep(30)
                    continue
                else:
                    break
            if data_row != "":
                fo.write(data_row + '\n')
            count += 1


def main():
    debug = False
    delimiter = '|'
    count = 1
    # for i in range(9, 25):
        # print(i)
    query_and_write(0)



    # locator_number = '19U410063'
    # year = '2024'
    # page = get_parcel_year_amount_owed(locator_number, year)
    # # taxes = parse_last_tax_year(page)
    # # print("got value:", taxes)


    # locator_number = '11G330915'
    # locator_number = '19U410063'
    # year = '2024'
    # history_total = get_total_owed_history(locator_number, year)
    # print("total owed for", locator_number, history_total)


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
