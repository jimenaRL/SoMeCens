import os
import csv
import yaml

from somecens import DemoGraph
from somecens.tools import \
    searchOccurrences, \
    matchUsersLocations

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

BANNEDWORDS = ["États-Unis", "Egypte"]


def test_searchOccurrences():

    file_path = os.path.join(DATADIR, "metadata.csv")
    search_col = "location"

    regex = "\\bLe Caire\\b"
    matchs = searchOccurrences(
        file_path,
        regex=regex,
        search_col=search_col,
        banned_regex=["\\bEgypte\\b"])
    assert len(matchs) == 0

    regex = ["\\bVal-d'Oise\\b", "\\bArica\\b"]
    matchs = searchOccurrences(
        file_path,
        regex=regex,
        search_col=search_col)
    assert len(matchs) == 1


def test_matchUsersLocations():

    # test users locations matchs
    matchedUsersLocs = matchUsersLocations(
        locations=LOCATIONSDICT,
        data=METADATA,
        banned_words=BANNEDWORDS,
        **MATCHKWARGS
    )

    for code, label in LOCATIONSDICT.items():
        s = f"""
            ------------
            code: {code}
            label: {label}
            # users expected: {MATCHNUMBERS[code]}
            # matched users: {len(matchedUsersLocs[code])}
            matchs:
            \t{'\n\t\t'.join([u[1] + " | " + u[2] for u in matchedUsersLocs[code]])}
            ------------"""
        print(s)
        if MATCHNUMBERS[code] != len(matchedUsersLocs[code]):
            m = f"Expected {MATCHNUMBERS[code]} matchs in data for location "
            m += f"'{code}: {label}', found {len(matchedUsersLocs[code])}:"
            m += f"\n\t{matchedUsersLocs[code]}"
            raise ValueError(m)


def test_matchMultipleUsersLocations():

    # test multiple users locations matchs
    multiUsersLocs = matchUsersLocations(
        locations=LOCATIONSDICTGROUPS,
        data=METADATA,
        banned_words=BANNEDWORDS,
        **MATCHKWARGS
    )

    for code, labels_list in LOCATIONSDICTGROUPS.items():
        s = f"""
            ------------
            code: {code}
            labels list: {labels_list}
            XXXX: {LOCATIONSDICT[code]}
            # matched users: {len(multiUsersLocs[code])}
            matchs:
                \t{'\n\t\t'.join([u[1] + " | " + u[2] for u in multiUsersLocs[code]])}
            ------------"""
        print(s)


if __name__ == "__main__":

    test_searchOccurrences()
    test_matchUsersLocations()
    test_matchMultipleUsersLocations()
