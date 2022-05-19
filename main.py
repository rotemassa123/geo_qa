import requests
import lxml.html
import urllib

URL_TO_COUNTRIES = " https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
XPATH_TO_COUNTRIES = "/html/body/div[3]/div[3]/div[5]/div[1]/table/tbody/tr/td[1]//a[1]/@href"

def format_country_name(country):
    country = country.replace("_", " ").replace("The ", "")
    return urllib.parse.unquote(country)

def get_countries(doc):
    countries = []
    for element in doc.xpath(XPATH_TO_COUNTRIES):
        elem_string = str(element).split('/')
        if not elem_string[0]:
            countries.append(format_country_name(elem_string[-1]))
    countries.sort()
    return countries


def main():
    url = requests.get(URL_TO_COUNTRIES)
    doc = lxml.html.fromstring(url.content)
    countries = get_countries(doc)

if __name__ == '__main__':
    main()
