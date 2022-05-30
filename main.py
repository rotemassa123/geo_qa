import time
import requests
import lxml.html
import urllib
from rdflib import Graph, Literal, URIRef
from Entities.Country import *
import CountryNames

RDF_URI_PREFIX = "http://example.org/"
URL_TO_COUNTRIES = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
XPATH_TO_COUNTRIES = "//table[@class='wikitable sortable static-row-numbers plainrowheaders srn-white-background']//tr/td[1]/span/a[1]/@href | //table[@class='wikitable sortable static-row-numbers plainrowheaders srn-white-background']//tr/td[1]/i/a[1]/@href | //table[@class='wikitable sortable static-row-numbers plainrowheaders srn-white-background']//tr/td[1]/span[@class = 'flagicon']/following-sibling::a[1]/@href"

def format_country_name(country_name):
    country_name = country_name.replace("The ", "")
    return urllib.parse.unquote(country_name)

def get_country(country_name):
    return Country(country_name)

def get_countries(doc):
    countries = {}
    country_names = CountryNames.get_country_names()

    for name in country_names:
        if not name in countries: #against duplicates
            countries[name] = Country(name)
            print(f"finished fetching {name} data")

    return countries


def add_country_to_ontology(g, country):
    country_literal = URIRef(RDF_URI_PREFIX + country.name)
    g.add((country_literal, URIRef(RDF_URI_PREFIX + "population"), Literal(country.population)))
    g.add((country_literal, URIRef(RDF_URI_PREFIX + "area"), Literal(country.area)))
    g.add((country_literal, URIRef(RDF_URI_PREFIX + "capital"), Literal(country.capital)))

    for form in country.gov_form:
        g.add((country_literal, URIRef(RDF_URI_PREFIX + "government_form"), Literal(form)))

    if country.president:
        president_literal = URIRef(RDF_URI_PREFIX + country.president.name)
        g.add((president_literal, URIRef(RDF_URI_PREFIX + "birth_location"),
               Literal(country.president.birth_loc)))
        g.add((president_literal, URIRef(RDF_URI_PREFIX + "birth_date"),
               Literal(country.president.date_of_birth)))

    if country.prime_minister:
        prime_minister_literal = URIRef(RDF_URI_PREFIX + country.prime_minister.name)
        g.add((prime_minister_literal, URIRef(RDF_URI_PREFIX + "birth_location"),
               Literal(country.prime_minister.birth_loc)))
        g.add((prime_minister_literal, URIRef(RDF_URI_PREFIX + "birth_date"),
               Literal(country.prime_minister.date_of_birth)))


def create_ontologies(countries):
    g = Graph()
    for country in countries.values():
        add_country_to_ontology(g, country)
        print(f"finished building {country.name} ontology")

    g.serialize(destination="ontology.nt")


def get_all_data():
    url = requests.get(URL_TO_COUNTRIES)
    doc = lxml.html.fromstring(url.content)
    return get_countries(doc)

def send_xpath(country_name, xpath):
    url = requests.get(f"https://en.wikipedia.org/wiki/{country_name}")
    doc = lxml.html.fromstring(url.content)

    for elem in doc.xpath(xpath):
        print(str(elem))


def test():
    country = get_country("Guam")
    create_ontologies({"Guam" : country})
    print("finished")

def test_results(countries):
    with open("log.txt", 'w') as f:
        for country in countries.values():
            if not country.area:
                f.write(f"{country.name} has area: {country.area}\n")
            if not country.population:
                f.write(f"{country.name} has population: {country.population}\n")
            if not country.capital:
                f.write(f"{country.name} has capital {country.capital}\n")
            if not country.gov_form:
                f.write(f"{country.name} has gov_form: {country.gov_form}\n")
            if not country.president and not country.prime_minister:
                f.write(f"{country.name} has no president and no prime minister\n")

if __name__ == '__main__':
    isTestRun = True
    shouldTestResults = True
    if isTestRun:
        test()
    else:
        start = time.time()
        countries = get_all_data()
        create_ontologies(countries)
        end = time.time()
        if(shouldTestResults):
            test_results(countries)
        print("time elapsed:", end - start)

