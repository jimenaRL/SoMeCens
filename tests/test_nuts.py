import json
import random

from somecens.nuts.tools import \
    COUNTRYCODES, \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions

def test_geounits(country, year):
    dicts = getUnits(country=country, year=year)
    l = len(dicts)
    n = random.randint(0, l)
    unit_dict = dicts[n]
    print("--- getUnits test")
    print(f"There are {l} dicts entries of the form:")
    print(json.dumps(unit_dict, indent=2))

def test_laus(country):
    laus = getLaus(country=country)
    l = len(laus)
    n = random.randint(0, l)
    key = list(laus.keys())[n]
    value = list(laus.values())[n]
    print("--- getLaus test")
    print(f"Dictionary of LAUS contains {l} entries of the form:")
    # print(f"\t{key}: {value}")
    print(json.dumps({key: value}, indent=2))

def test_age_distribution(country, year):
    aDist = getNutsAgeDistributions(country=country, year=year)
    l = len(aDist)
    n = random.randint(0, l)
    print("--- getNutsAgeDistributions test")
    print(f"Age distributions list contains {len(aDist)} entries of the form:")
    print(json.dumps(aDist[n], indent=2))

def test_gender_distribution(country, year):
    gDist = getNutsGenderDistributions(country=country, year=year)
    l = len(gDist)
    n = random.randint(0, l)
    print("--- getNutsGenderDistributions test")
    print(f"Gender distributions list contains {len(gDist)} entries of the form:")
    print(json.dumps(gDist[n], indent=2))

if __name__ == "__main__":

    year = 2024
    country = 'france'
    s = f"----- NUTS MODULE TEST | COUNTRY {country} | NUTS {year} -----"
    print(f"{'-' * len(s)}\n{s}\n{'-' * len(s)}")

    test_geounits(country, year)
    test_laus(country)
    test_age_distribution(country, year)
    test_gender_distribution(country, year)
