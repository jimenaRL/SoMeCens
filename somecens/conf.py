import os
import csv
import yaml

DIRPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDERPATH = os.path.join(DIRPATH, "data")


with open(os.path.join(DATAFOLDERPATH, "pays_capitales.csv")) as f:
    PAYS = {d["country"] for d in csv.DictReader(f)}

with open(os.path.join(DATAFOLDERPATH, "geocodes_countries_capitals.csv")) as f:
    COUNTRIES = {d["Country"] for d in csv.DictReader(f)}

with open(os.path.join(DATAFOLDERPATH, "country_aliases.yml")) as f:
    COUNTRYALIASES = yaml.safe_load(f)
