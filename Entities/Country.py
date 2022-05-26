from Entities.Person import Person
import requests
import lxml.html
import urllib

WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"


class Country:
    def __init__(self, name):
        self.name = name

        url = WIKIPEDIA_PREFIX + name.replace(" ", "_")
        self.doc = lxml.html.fromstring(requests.get(url).content)

        self.president = self.get_president()
        self.prime_minister = self.get_prime_minister()

        self.population = self.get_population()
        self.area = self.get_area()
        self.gov_form = self.get_gov_form()
        self.capital = self.get_capital()

    def get_president_name(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'President']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_prime_minister_name(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'Prime " \
                "Minister']/td/a/text() "
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_population(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/a/text() " \
                "='Population']/following-sibling::*[1]/td/text() "
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_area(self):  # TODO: need to check about the area being squared!
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/a/text() ='Area ']/following-sibling::*[" \
                "1]/td/text() "
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_gov_form(self):
        gov_forms = []
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[./th/a[text()='Government']]/td/a/text()"
        "| tr[./th/a[text()='Government']]/td/span/a/text()"
        "| tr[./th/text()='Government']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            gov_forms.append(str(elem))

        return gov_forms

    def get_capital(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/text() = 'Capital']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_president(self):
        name = self.get_president_name()
        return Person(name) if name else None

    def get_prime_minister(self):
        name = self.get_prime_minister_name()
        return Person(name) if name else None
