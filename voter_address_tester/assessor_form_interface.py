import mechanicalsoup


def get_owner_name_from_address(address):

    browser = mechanicalsoup.StatefulBrowser(user_agent='MechanicalSoup')
    browser.open("https://www.stlouis-mo.gov/data/address-search/index.cfm")

    # Fill-in the search form
    browser.select_form(nr=1)
    browser["streetAddress"] = address
    browser.submit_selected()
    property_owners = browser.page.find(text='Owner name').findNext('td').text
    print(property_owners)
    return property_owners


def main():
    data_file_location = "data/city voters non-apts - CountyWide_VotersList_08202020_.csv" # noQA
    output_file_location = "data/output.csv"

    street_number_idx = 3
    street_name_idx = 5
    street_type_idx = 6

    with open(data_file_location) as data_file:
        with open(output_file_location, 'w') as o:
            for line in data_file:
                output_line = line[:-1]
                print(line)
                fields = line.split(',')
                assembled_address = ''
                assembled_address += fields[street_number_idx] + ' '
                assembled_address += fields[street_name_idx] + ' '
                assembled_address += fields[street_type_idx]
                print(assembled_address)
                owners = get_owner_name_from_address(assembled_address)
                output_line += owners + '\n'
                o.write(output_line)


if __name__ == '__main__':
    main()
