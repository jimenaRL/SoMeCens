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
from somecens.tools import matchUsersLocations, matchUsersMultipleLocations

DEFAULTYEAR = 2024
DEFAULTMETAYEAR = 2020
DEFAULTCOUNTRY = 'france'
# METADATADB = f'{country}_2020_pseudonymized_alldata.db'
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/${country}_${metadata_year}_pseudonymized_alldata.db"

ap = ArgumentParser (prog="Test script for some4dem")
ap.add_argument('--country', required=False, type=str, default=DEFAULTCOUNTRY)
ap.add_argument('--year', required=False, type=str, default=DEFAULTYEAR)
ap.add_argument('--metadata_year', required=False, type=str, default=DEFAULTMETAYEAR)
ap.add_argument('--dbpath', required=False, type=str, default=DEFAULTDBPATTERN)

args = ap.parse_args()
country = args.country
year = args.year
metadata_year = args.metadata_year
dbpath = Template(args.dbpath).safe_substitute(
    country=country,
    metadata_year=metadata_year)

s = f"----- {country.upper()} nuts_{year} metadata_{metadata_year} -----"
print(f"{'-' * len(s)}\n{s}\n{'-' * len(s)}")

nuts_geo_units = getUnits(country, year=year)
laus = getLaus('france')

demo = DemoGraph(demography=nuts_geo_units)
demo.setSubUnitsNames(laus)
# demo.getGeoUnit(code='FR10').indentPrint()

code = "FRK21"
label = "Ile-de-France"
# print(f"The label of the NUTS code '{code}' is: '{demo.findLabelFromCode(code)}'")
# print(f"The NUTS codes associated to the label '{label}' are: {demo.findCodesFromLabel(label)}")
demo.showGeoUnits(max_level=1)

geoUnit = demo.getGeoUnit(code='FRJ')
getUnit_descendants = demo.getDescendants(geoUnit)

genderDist = getNutsGenderDistributions(country, year=year)
demo.setGenderDistributions(genderDist)
demo.showGeoUnits(max_level=1)

ageDist = getNutsAgeDistributions(country, year=year)
demo.setAgeDistributions(ageDist)
demo.showGeoUnits(max_level=1)

exit()


columns = ['pseudo_id', 'location']
metadata = getMetadata(dbpath, columns)

# test users locations matchs
usersLocations = matchUsersLocations(
    locations=demo.locations,
    metadata=metadata,
    stopwords=["le", "la", "de"],
    search_index=1,
    method='regex'
)
demo.setUsersLocations(usersLocations)
localizedUsersDict = demo.getLocalizedUsers(code="FRJ24", descendants=True)
print("Localized users number:")
for loc in localizedUsersDict:
     print("    " + loc + " " + demo.getGeoUnit(code=loc).label + " " + str(len(localizedUsersDict[loc])))
     for u in localizedUsersDict[loc][-5:]:
         print("            " + u[0] + " " + f"'{u[1]}'")

for g in demo.geoUnits:
    print(f"code: {g.code} | label: {g.label} | users found: {len(usersLocations[g.code])}")

# test multiple users locations matchs
demo = DemoGraph(demography=geo_units)
demo.setSubUnitsNames(laus)
lausUsersLocations = matchUsersMultipleLocations(
    locations_groups=demo.getSubUnits(),
    metadata=metadata,
    stopwords=["le", "la", "de"],
    search_index=1,
    method='regex'
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


import pandas as pd
allLocalizedUsersDictMulti = demo.getLocalizedUsers(code="FR", descendants=True)
for loc in allLocalizedUsersDictMulti:
    length = str(len(allLocalizedUsersDictMulti[loc]))
    label = demo.getGeoUnit(code=loc).label[:15]
    pd.DataFrame(data=allLocalizedUsersDictMulti[loc]).to_csv("results/20250710/"+loc+"_"+label+"_"+length+".csv")

#for level in [1, 2, 3]:
#    demo.exportLocalizationsMatches(
#        path=f'nb_matchs_{country}_nuts_{level}.csv',
#        level=level
#    )


