import os
import csv
import yaml

from somecens import DemoGraph
from somecens.nuts.tools import \
    COUNTRYCODES, \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions
from somecens.epo.tools import getMetadata
from somecens.tools import matchUsersLocations, matchUsersMultipleLocations

DEFAULTYEAR = 2024
DEFAULTMETAYEAR = 2020
DEFAULTCOUNTRY = 'france'
# METADATADB = f'{country}_2020_pseudonymized_alldata.db'
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/${country}_${metadata_year}_pseudonymized_alldata.db"

country = DEFAULTCOUNTRY
year = DEFAULTYEAR
metadata_year = DEFAULTMETAYEAR
dbpath = "france_2023_pseudonymized_alldata.db"

dir_path = os.path.dirname(os.path.realpath(__file__))
geounits_path = os.path.join(dir_path, "data", "geounits.yml")
DATADIR = os.path.join(dir_path, "data")

with open(os.path.join(DATADIR, "geounits.yml")) as f:
    GEOUNITS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "subunits.yml")) as f:
    SUBUNITS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "metadata.csv")) as f:
    METADATA = [r for r in csv.reader(f)]

with open(os.path.join(DATADIR, "user_locations.yml")) as f:
    USERLOCATIONS = yaml.safe_load(f)

with open(os.path.join(DATADIR, "expected_match_numbers.yml")) as f:
    MATCHNUMBERS = yaml.safe_load(f)


DEMO = DemoGraph(demography=GEOUNITS)
DEMO.setSubUnitsNames(SUBUNITS)
LOCATIONSDICT = {d["code"]: d["label"] for d in GEOUNITS}
LOCATIONSDICTGROUPS = DEMO.getSubUnits(),

def test_matchUsersLocations():

    # test users locations matchs
    usersLocations = matchUsersLocations(
        locations=LOCATIONSDICT,
        metadata=METADATA,
        stopwords=["le", "la", "de"],
        search_index=1,
        method='regex'
    )
    for code, label in LOCATIONSDICT.items():
        print(f"code: {code} | label: {label} | # users found: {len(usersLocations[code])}")
        assert MATCHNUMBERS[code] == len(usersLocations[code])


def matchUsersMultipleLocations():

    lausUsersLocations = matchUsersMultipleLocations(
        locations_groups=LOCATIONSDICTGROUPS,
        metadata=metadata,
        stopwords=["le", "la", "de"],
        search_index=1,
        method='regex'
    )
    # TO CHECK AND MAKE PROPER TEST
    assert 1 == 0

if __name__ == "__main__":

    s = f"----- LOCATIONS MATCH METHODS TEST -----"

    test_matchUsersLocations()
    matchUsersMultipleLocations()


