# =============================================================================
# NUTS tools tests
# =============================================================================
#

import json
import random

from somecens.nuts.tools import \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions

COUNTRY = "france"
YEAR = 2024


def test_geounits(country=COUNTRY, year=YEAR):
    dicts = getUnits(country=country, year=year)
    length = len(dicts)
    n = random.randint(0, length)
    unit_dict = dicts[n]
    assert isinstance(dicts, list)
    assert isinstance(unit_dict, dict)
    print("--- getUnits test")
    print(f"There are {length} dicts entries of the form:")
    print(json.dumps(unit_dict, indent=2))


def test_laus(country=COUNTRY):
    laus = getLaus(country=country)
    length = len(laus)
    n = random.randint(0, length)
    key = list(laus.keys())[n]
    value = list(laus.values())[n]
    assert isinstance(laus, dict)
    assert isinstance(value, list)
    print("--- getLaus test")
    print(f"Dictionary of LAUS contains {length} entries of the form:")
    # print(f"\t{key}: {value}")
    print(json.dumps({key: value}, indent=2))


def test_age_distribution(country=COUNTRY, year=YEAR):
    aDist = getNutsAgeDistributions(country=country, year=year)
    length = len(aDist)
    n = random.randint(0, length)
    assert isinstance(aDist, list)
    assert isinstance(aDist[n], dict)
    print("--- getNutsAgeDistributions test")
    print(f"Age distributions list contains {length} entries of the form:")
    print(json.dumps(aDist[n], indent=2))


def test_gender_distribution(country=COUNTRY, year=YEAR):
    gDist = getNutsGenderDistributions(country=country, year=year)
    length = len(gDist)
    n = random.randint(0, length)
    print("--- getNutsGenderDistributions test")
    print(f"Gender distributions list contains {length} entries of the form:")
    print(json.dumps(gDist[n], indent=2))


if __name__ == "__main__":

    country = COUNTRY
    year = YEAR

    s = f"----- NUTS MODULE TEST | COUNTRY {country} | NUTS {year} -----"
    print(f"{'-' * len(s)}\n{s}\n{'-' * len(s)}")

    test_geounits(country, year)
    test_laus(country)
    test_age_distribution(country, year)
    test_gender_distribution(country, year)
