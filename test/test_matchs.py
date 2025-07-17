import os
import csv
import yaml

from somecens import DemoGraph
from somecens.tools import \
    searchOccurrences, \
    matchUsersLocations, \
    matchUsersMultipleLocations

dir_path = os.path.dirname(os.path.realpath(__file__))
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
LOCATIONSDICTGROUPS = DEMO.getSubUnits()

MATCHKWARGS = {
    "stopwords": ["le", "la", "de"],
    "split_characters": ["-"],
    "search_index": 1,
    "has_headers": True
}

def test_searchOccurrences():

    regex = "\\bVal-d'Oise\\b"
    file_path = os.path.join(DATADIR, "metadata.csv")
    matchs = searchOccurrences(file_path, regex=regex, search_col="location")
    assert len(matchs) == 1
    s = f"regex: {regex} | # matchs: {len(matchs)} | matchs: {matchs}"
    print(s)

def test_matchUsersLocations():

    # test users locations matchs
    usersLocations = matchUsersLocations(
        locations=LOCATIONSDICT,
        data=METADATA,
        **MATCHKWARGS
    )

    for code, label in LOCATIONSDICT.items():
        s = f"""
            ------------
            code: {code}
            label: {label}
            # users expected: {MATCHNUMBERS[code]}
            # matched users: {len(usersLocations[code])}
            matchs:\n\t\t{'\n\t\t'.join([u[1]+" | "+u[2] for u in usersLocations[code]])}
            ------------"""
        print(s)
        if MATCHNUMBERS[code] != len(usersLocations[code]):
            m = f"Expected {MATCHNUMBERS[code]} matchs in data for location "
            m += f"'{code}: {label}', found {len(usersLocations[code])}:"
            m += f"\n\t{usersLocations[code]}"
            raise ValueError(m)

def test_matchUsersMultipleLocations():

    multipleUsersLocations = matchUsersMultipleLocations(
        locations_groups=LOCATIONSDICTGROUPS,
        data=METADATA,
        **MATCHKWARGS
    )

    for code, label in LOCATIONSDICT.items():
        s = f"""
            ------------
            code: {code}
            label: {label}
            # matched users: {len(multipleUsersLocations[code])}
            matchs:\n\t\t{'\n\t\t'.join([u[1]+" | "+u[2] for u in multipleUsersLocations[code]])}
            ------------"""
        print(s)

if __name__ == "__main__":

    test_searchOccurrences()
    test_matchUsersLocations()
    test_matchUsersMultipleLocations()


