import mechanicalsoup


def get_owner_name_from_address(address):

    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    browser.open("https://www.stlouis-mo.gov/data/address-search/index.cfm")

    # Fill-in the search form
    browser.select_form(nr=1)
    browser["streetAddress"] = address
    browser.submit_selected()
    owner_name = browser.page.find(text='Owner name')
    results_table = browser.page.find('table', id='address-search')
    if owner_name is not None:
        property_owners = owner_name.findNext('td').text
    elif results_table is not None:
        property_owners = '-ambiguous-'

        for disambiguate in results_table.find_all('tr'):
            if len(disambiguate.find_all('td')) > 1:
                property_owners += ';'
                property_owners += disambiguate.find_all('td')[2].text
            else:
                # assuming this is header row
                pass
                print(disambiguate.find_all('td'))
    else:
        property_owners = 'Error'
    print(property_owners)
    return property_owners


def iterate_addresses():
    data_file_location = "data/city voters non-apts - CountyWide_VotersList_08202020_.csv" # noQA
    output_file_location = "data/output.csv"

    street_number_idx = 3
    street_prefix_idx = 4
    street_name_idx = 5
    resident_last_name_idx = 2
    line_count = 0

    with open(data_file_location) as data_file:
        with open(output_file_location, 'w') as o:
            for line in data_file:
                line_count += 1
                hit = False
                output_line = str(line_count) + ','
                output_line += line[:-1]
                print(line)
                fields = line.split(',')
                assembled_address = ''
                assembled_address += fields[street_number_idx] + ' '
                if not fields[street_prefix_idx] == '':
                    assembled_address += fields[street_prefix_idx] + ' '
                assembled_address += fields[street_name_idx]
                print(assembled_address)
                owners = get_owner_name_from_address(assembled_address)
                if fields[resident_last_name_idx] in owners:
                    hit = True
                output_line += ',' + str(hit)
                output_line += ',' + owners
                output_line += '\n'

                o.write(output_line)


def main():
    # print(get_owner_name_from_address('4095 wilmington'))
    # get_owner_name_from_address('19 N BOYLE')
    iterate_addresses()

if __name__ == '__main__':
    main()
