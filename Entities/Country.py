from Entities.PrimeMinister import PrimeMinister
from Entities.President import President
import requests
import lxml.html
import urllib

WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"


class Country:
    def __init__(self, name):
        self.name = name

        name = name.replace(" ", "_")
        self.url = WIKIPEDIA_PREFIX + name
        self.doc = lxml.html.fromstring(requests.get(self.url).content)

    def set_values(self):
        print(self.get_president_name(), self.get_prime_minister_name())

    def get_president_name(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'President']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            return elem

    def get_prime_minister_name(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/div/a/text() = 'Prime Minister']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            return elem