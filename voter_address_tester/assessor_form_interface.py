from activesoup import driver

d = driver.Driver()
assesssor_URL = 'https://www.stlouis-mo.gov/data/address-search/index.cfm'
assessor_search_page = d.get(assesssor_URL)

search_form = assessor_search_page.form
search_value = {'streetAddress': '5100 DRESDEN AV'}
address_search_result = search_form.submit(search_value)


if address_search_result.response.status_code not in range(200, 300):
    raise RuntimeError("no search result")

# got a result

# print(address_search_result.find_all('div')[0].text)
print(address_search_result.url)
