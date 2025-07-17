import csv
from argparse import ArgumentParser
from string import Template

from somecens import DemoGraph
from somecens.nuts.tools import \
    COUNTRYCODES, \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions
from somecens.epo.tools import getMetadata
from somecens.tools import matchUsersLocations

MATCHKWARGS = {
    "stopwords": ["le", "la", "de"],
    "split_characters": ["-"],
    "search_index": 1,
    "has_headers": False
}

DEFAULTYEAR = 2024
DEFAULTMETAYEAR = 2020
DEFAULTCOUNTRY = 'france'
# METADATADB = f'{country}_2020_pseudonymized_alldata.db'
# DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/${country}_${metadata_year}_pseudonymized_alldata.db"


# ap = ArgumentParser (prog="Test script for some4dem")
# ap.add_argument('--country', required=False, type=str, default=DEFAULTCOUNTRY)
# ap.add_argument('--year', required=False, type=str, default=DEFAULTYEAR)
# ap.add_argument('--metadata_year', required=False, type=str, default=DEFAULTMETAYEAR)
# ap.add_argument('--dbpath', required=False, type=str, default=DEFAULTDBPATTERN)

# args = ap.parse_args()
# country = args.country
# year = args.year
# metadata_year = args.metadata_year
# dbpath = Template(args.dbpath).safe_substitute(
#     country=country,
#     metadata_year=metadata_year)


year = DEFAULTYEAR
metadata_year = DEFAULTMETAYEAR
country = DEFAULTCOUNTRY
dbpath = f'{country}_2020_pseudonymized_alldata.db'

with open('somecens/data/pays_capitales.csv') as f:
    reader = csv.DictReader(f)
    countries = [r["country"] for r in reader]

metadata = getMetadata(
    dbpath,
    columns=['pseudo_id', 'location'],
    not_null="location",
    limit=1000)

demo = DemoGraph(demography=getUnits(country, year))
demo.setSubUnitsNames(getLaus(country))

lausLocations = demo.getSubUnits()

lausUsersLocations = matchUsersLocations(
        locations=lausLocations,
        data=metadata,
        banned_words=countries,
        **MATCHKWARGS
    )

demo.setUsersLocations(lausUsersLocations)
localizedUsersDictMulti = demo.getLocalizedUsers(code="FRJ2", descendants=True)
print("Localized users number:")
for loc in localizedUsersDictMulti:
    print("    " + loc + " " + demo.getGeoUnit(code=loc).label + " " + str(len(localizedUsersDictMulti[loc])))
    for u in localizedUsersDictMulti[loc][-15:]:
        print("            " + u[0] + " " + f"'{u[1]}'")


for g in demo.geoUnits:
    print(f"code: {g.code} | label: {g.label} | users found: {len(lausUsersLocations[g.code])}")


# TO DO : make expors
# import pandas as pd
# allLocalizedUsersDictMulti = demo.getLocalizedUsers(code="FR", descendants=True)
# for loc in allLocalizedUsersDictMulti:
#     length = str(len(allLocalizedUsersDictMulti[loc]))
#     label = demo.getGeoUnit(code=loc).label[:15]
#     pd.DataFrame(data=allLocalizedUsersDictMulti[loc]).to_csv("results/20250710/"+loc+"_"+label+"_"+length+".csv")

#for level in [1, 2, 3]:
#    demo.exportLocalizationsMatches(
#        path=f'nb_matchs_{country}_nuts_{level}.csv',
#        level=level
#    )


