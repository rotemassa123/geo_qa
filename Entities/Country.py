from Entities.PrimeMinister import PrimeMinister
from Entities.President import President

WIKIPEDIA_PREFIX = "https://en.wikipedia.org/wiki/"


class Country:
    def __init__(self, name):
        self.name = name

        name = name.replace(" ", "_")
        self.url = WIKIPEDIA_PREFIX + name

    @classmethod
    def set_values(cls):
        cls.prime_minister = PrimeMinister.set_values()
        cls.president = President.set_values()
