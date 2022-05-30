from Entities.Person import Person
import requests
import lxml.html
import urllib

WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"
BASE_QUERY = "//table[contains(@class, 'infobox')]/tbody"

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
        xpath = BASE_QUERY + "/tr[th/div/a/text() = 'President']/td/a/@href" + " | " + BASE_QUERY + "/tr[th/div/a/text() = 'President']/td/span/a[1]/@href"
        for elem in self.doc.xpath(xpath):
            return str(elem).split("/")[-1]

    def get_prime_minister_name(self):
        xpath = BASE_QUERY + "/tr[th/div/a/text() = 'Prime Minister']/td/a/@href "
        for elem in self.doc.xpath(xpath):
            return str(elem).split("/")[-1]

    def get_population(self):
        xpath = BASE_QUERY + "/tr[th/a/text() ='Population']/following-sibling::*[1]/td//text()" + " | " + BASE_QUERY + "/tr[th/text() ='Population']/following-sibling::*[1]/td//text()" + " | " + BASE_QUERY + "tr[th/text() ='Population']/td//text()"
        for elem in self.doc.xpath(xpath):
            population = str(elem)
            if not population or population == ' ' or population == ' (' or population == ')'  or '/' in population:
                continue
            return population.replace(" ", "")

    def get_area(self):  # TODO: need to check about the area being squared!
        xpath = BASE_QUERY + "/tr[th/a/text() ='Area']/following-sibling::*[1]/td/text()" + " | " + BASE_QUERY + "/tr[th/a/text() ='Area ']/following-sibling::*[1]/td/text()" " | " + BASE_QUERY + "/tr[th/text() ='Area']/following-sibling::*[1]/td/text()"
        for elem in self.doc.xpath(xpath):
            if self.name == 'American_Samoa':
                return str(elem)[:2]
            return str(elem).replace(" ", "")

    def get_gov_form(self):
        gov_forms = []
        xpath = BASE_QUERY + "/tr[th//text()='Government']/td//a[not(contains(@href,'#cite'))]/@href"
        for elem in self.doc.xpath(xpath):
            gov_forms.append(str(elem).split("/")[-1].replace(" ", "_"))

        return gov_forms

    def get_capital(self):
        xpath = BASE_QUERY + "/tr[th/text() = 'Capital']/td/a/@href" + " | " + BASE_QUERY + "/tr[th/text() = 'Capital']/td/div/ul/li/a[1]/@href"
        for elem in self.doc.xpath(xpath):
            return str(elem).split("/")[-1].replace(" ", "_")

    def get_president(self):
        name = self.get_president_name()
        return Person(name) if name else None

    def get_prime_minister(self):
        name = self.get_prime_minister_name()
        return Person(name) if name else None
