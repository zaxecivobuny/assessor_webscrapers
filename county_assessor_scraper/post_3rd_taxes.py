import tax_fetcher

from tax_fetcher import fetch_tax_page_by_locator_number_requests



def main():
    locator_number = '11G330915'
    year = '2024'
    print(fetch_tax_page_by_locator_number_requests(locator_number, year))

    # Billing1 > div:nth-child(2) > div:nth-child(2) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)

if __name__ == '__main__':
    main()
