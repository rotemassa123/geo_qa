import lxml.html
import requests

WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"

class Person:
    def __init__(self, name):
        self.name = name

        url = WIKIPEDIA_PREFIX + name.replace(" ", "_")
        self.doc = lxml.html.fromstring(requests.get(url).content)

        self.date_of_birth = self.get_date_of_birth()
        self.birth_loc = self.get_birth_loc()

    def get_date_of_birth(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/text() = 'Born']/td/span/span/text()"
        for elem in self.doc.xpath(xpath):
            return str(elem)

    def get_birth_loc(self):
        xpath = "/html/body/div[3]/div[3]/div[5]/div[1]/table[1]/tbody/tr[th/text() = 'Born']/td/a/text()"
        for elem in self.doc.xpath(xpath):
            return str(elem)
