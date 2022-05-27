import time
import requests
import lxml.html
import urllib
from rdflib import Namespace, Graph, Literal, URIRef, FOAF

from Entities.Country import Country

RDF_URI_PREFIX = "http://example.org/"
URL_TO_COUNTRIES = "https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations)"
XPATH_TO_COUNTRIES = "/html/body/div[3]/div[3]/div[5]/div[1]/table/tbody/tr/td[1]//a[1]/@href"


def format_country_name(country_name):
    country_name = country_name.replace("The ", "")
    return urllib.parse.unquote(country_name)


def get_countries(doc):
    countries = {}
    for element in doc.xpath(XPATH_TO_COUNTRIES):
        elem_string = str(element).split('/')
        if not elem_string[0]:
            name = format_country_name(elem_string[-1])
            if not name in countries:
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
        g.add((Literal(country.president.name), URIRef(RDF_URI_PREFIX + "birth_location"),
               Literal(country.president.birth_loc)))
        g.add((Literal(country.president.name), URIRef(RDF_URI_PREFIX + "birth_date"),
               Literal(country.president.date_of_birth)))

    if country.prime_minister:
        g.add((Literal(country.prime_minister.name), URIRef(RDF_URI_PREFIX + "birth_location"),
               Literal(country.prime_minister.birth_loc)))
        g.add((Literal(country.prime_minister.name), URIRef(RDF_URI_PREFIX + "birth_date"),
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


def test():
    url = requests.get("https://en.wikipedia.org/wiki/Naftali_Bennett")
    doc = lxml.html.fromstring(url.content)

    xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/text() = 'Born']/td/span/span/text()"
    for elem in doc.xpath(xpath):
        print(str(elem))


if __name__ == '__main__':
    start = time.time()
    countries = get_all_data()
    create_ontologies(countries)
    end = time.time()
    print("time elapsed:", end - start)
    # test()
