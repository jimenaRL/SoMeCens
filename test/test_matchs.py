import os
import csv
import yaml
import json

from somecens import DemoGraph
from somecens.tools import \
    reverseSearch, \
    searchOccurrence, \
    searchOccurrences, \
    matchUsersLocations

dir_path = os.path.dirname(os.path.realpath(__file__))
TESTDATADIR = os.path.join(dir_path, "data")

with open(os.path.join(TESTDATADIR, "geounits.yml")) as f:
    GEOUNITS = yaml.safe_load(f)

with open(os.path.join(TESTDATADIR, "subunits.yml")) as f:
    SUBUNITS = yaml.safe_load(f)

with open(os.path.join(TESTDATADIR, "metadata.csv")) as f:
    METADATA = [r for r in csv.reader(f)]

with open(os.path.join(TESTDATADIR, "user_locations.yml")) as f:
    USERLOCATIONS = yaml.safe_load(f)

with open(os.path.join(TESTDATADIR, "expected_match_numbers.yml")) as f:
    MATCHNUMBERS = yaml.safe_load(f)

BANNEDREGEXFILE = os.path.join(TESTDATADIR, "country_regex.txt")
CSVFILE = os.path.join(TESTDATADIR, "metadata.csv")

with open('somecens/data/flags_unicode_emoji.json', 'r') as f:
    flags_unicode_emojis = json.load(f)

with open("somecens/data/franceFlags.txt", 'r') as f:
    french_flag_emojis = [d['name'] for d in csv.DictReader(f)]

banned_emojis = list(flags_unicode_emojis.values())
for f in french_flag_emojis:
    banned_emojis.remove(f)

BANNEDEMOJIES = list(flags_unicode_emojis.values())
BANNEDWORDS = ["Le Caire", "Australia"]


DEMO = DemoGraph(demography=GEOUNITS)
DEMO.setSubUnitsNames(SUBUNITS)
LOCATIONSDICT = {d["code"]: d["label"] for d in GEOUNITS}
LOCATIONSDICTGROUPS = DEMO.getAllSubUnits(max_level=3)

MATCHKWARGS = {
    "stopwords": ["le", "la", "de"],
    "split_characters": ["-"],
    "search_index": 1,
    "has_headers": True
}

SEARCHCOL = "location"

def test_reverseSearch():
    output = reverseSearch(
        csvfile=CSVFILE,
        search_col=SEARCHCOL,
        banned_regex_file=BANNEDREGEXFILE)
    # when countin lined of parsed output remove 1 for trailing '\n' and
    # another 1 for headers
    nb_not_removed = len(output.split("\n")) -1 - 1
    assert nb_not_removed == 43

def test_searchOccurrences():

    search_col = "location"

    regex = ["\\bVal-d'Oise\\b", "\\bArica\\b"]
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=[],
        banned_emojis=[],
    )
    assert len(matchs) == 1

    regex = ["\\bVal-d'Oise\\b", "\\bArica\\b"]
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=[],
        banned_emojis=[],
    )
    assert len(matchs) == 1

    BANNEDEMOJIES.remove(':France:')

    regex = ["\\bArica\\b", "\\bFrance\\b",]
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=[],
        banned_emojis=[],
    )
    assert len(matchs) == 7
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=french_flag_emojis,
        banned_emojis=BANNEDEMOJIES,
    )
    assert len(matchs) == 6

    regex = ["\\bBordeaux\\b",]
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=[],
        banned_emojis=[],
    )
    assert len(matchs) == 1
    matchs = searchOccurrences(
        csvfile=CSVFILE,
        regex=regex,
        search_col=SEARCHCOL,
        allowed_emojis=[],
        banned_emojis=BANNEDEMOJIES,
    )
    assert len(matchs) == 0


def test_matchUsersLocations():

    # test users locations matchs
    matchedUsersLocs = matchUsersLocations(
        locations=LOCATIONSDICT,
        data=METADATA,
        banned_words=BANNEDWORDS,
        allowed_emojis=french_flag_emojis,
        banned_emojis=BANNEDEMOJIES,
        **MATCHKWARGS
    )

    for code, label in LOCATIONSDICT.items():
        # s = f"""
        #     ------------
        #     code: {code}
        #     label: {label}
        #     # users expected: {MATCHNUMBERS[code]}
        #     # matched users: {len(matchedUsersLocs[code])}
        #     matchs:
        #     \t{'\n\t\t'.join([u[1] + " | " + u[2] for u in matchedUsersLocs[code]])}
        #     ------------"""
        # print(s)
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
    # for code, labels_list in LOCATIONSDICTGROUPS.items():
    #     s = f"""
    #         ------------
    #         code: {code}
    #         labels list: {labels_list}
    #         XXXX: {LOCATIONSDICT[code]}
    #         # matched users: {len(multiUsersLocs[code])}
    #         matchs:
    #             \t{'\n\t\t'.join([u[1] + " | " + u[2] for u in multiUsersLocs[code]])}
    #         ------------"""
    #     print(s)


if __name__ == "__main__":
    test_reverseSearch()
    # test_searchOccurrences()
    # test_matchUsersLocations()
    # test_matchMultipleUsersLocations()
