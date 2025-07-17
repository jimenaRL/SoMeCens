# =============================================================================
# Demograph and GeoUnit classes tests
# =============================================================================
#

import os
import csv
import json
import yaml
import pytest

from somecens import DemoGraph, GeoUnit

dir_path = os.path.dirname(os.path.realpath(__file__))
geounits_path = os.path.join(dir_path, "data", "geounits.yml")
DATADIR = os.path.join(dir_path, "data")

with open(os.path.join(DATADIR, "geounits.yml")) as f:
    GEOUNITS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "subunits.yml")) as f:
    SUBUNITS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "age_distribution.yml")) as f:
    AGEDIST = yaml.safe_load(f)

with open(os.path.join(DATADIR, "gender_distribution.yml")) as f:
    GENDERDIST = yaml.safe_load(f)

with open(os.path.join(DATADIR, "metadata.csv")) as f:
    METADATA = [r for r in csv.reader(f)]

with open(os.path.join(DATADIR, "user_locations.yml")) as f:
    USERLOCATIONS = yaml.safe_load(f)

def test_geoUnits():
    geoUnit = GeoUnit(**GEOUNITS[-1])
    geoUnit.indentPrint()

def test_bad_formatted_input_geounits():
    badUnit = {
        'country_code': 'XR',
        'code': 'ZRY22',
        'level': '3',
        'label': 'Some label',
        'parent_code': 'YRY2'
    }
    BADGEOUNITS = GEOUNITS + [badUnit]
    with pytest.raises(Exception) as exc_info:
        demo = DemoGraph(demography=BADGEOUNITS)
    assert exc_info.value.args[0] == "There is no geoUnit with code 'YRY2'."

def test_demograph():

    demo = DemoGraph(demography=GEOUNITS)

    demo.setSubUnitsNames(SUBUNITS)
    demo.showGeoUnits(max_level=1)
    geoUnit = demo.getGeoUnit(code='FR1')
    getUnit_descendants = demo.getDescendants(geoUnit)

    # test bad request
    with pytest.raises(Exception) as exc_info:
        demo.getGeoUnit(code='GR1')
    assert exc_info.value.args[0] == "There is no geoUnit with code 'GR1'."

    demo.setGenderDistributions(GENDERDIST)
    demo.showGeoUnits(max_level=0)

    demo.setAgeDistributions(AGEDIST)
    demo.showGeoUnits(max_level=0)


def test_usersLocations():

    demo = DemoGraph(demography=GEOUNITS)
    demo.setUsersLocations(USERLOCATIONS)

    print("Localized users:")
    for loc, users in demo.getLocalizedUsers(code="FR", descendants=True).items():
         print("    " + loc + " " + demo.getGeoUnit(code=loc).label)
         for u in users:
             print("            " + u[0] + " " + f"'{u[1]}'")

# def test_checkDemography():
#     None

# def test_checkGenderDistributions():
#     None

if __name__ == "__main__":
    test_geoUnits()
    test_demograph()
    test_bad_formatted_input_geounits()
    test_usersLocations()


