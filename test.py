from somecens import DemoGraph
from somecens.nuts.tools import \
    getUnits, getNutsLocations, getNutsLocationsLevel, getNutsGenderDistributions, getNutsAgeDistributions
from somecens.epo.tools import getMetadata
from somecens.tools import matchUsersLocations

year = 2024
country = 'france'
metadata_year = 2020
print(f"----- {country} nuts_{year} metadata_{metadata_year} -----")

locs_level2_2024 = getNutsLocationsLevel(country, level=2, year=year)
locations = getNutsLocations(country, format='flatten', year=year)
geo_units = getUnits(country, year=year)

demo = DemoGraph(demography=geo_units)
# demo.showGeoUnits()
getUnit = demo.getGeoUnit(code='FRJ')
getUnit_descendants = demo.getDescendants(getUnit)

genderDist = getNutsGenderDistributions(country, year=year)
demo.setGenderDistributions(genderDist)
# demo.showGeoUnits()

ageDist = getNutsAgeDistributions(country, year=year)
demo.setAgeDistributions(ageDist)
# demo.showGeoUnits()

columns = ['pseudo_id', 'location']
metadata = getMetadata(f'{country}_2020_pseudonymized_alldata.db', columns)
usersLocations = matchUsersLocations(demo.locations, metadata, columns)

demo.setUsersLocations(usersLocations)
# demo.showGeoUnits()

demo.getGeoUnitByLabel(label='Aquitaine').indentPrint()
localizedUsersDict = demo.getLocalizedUsers(code="FRI1")
print("Localized users examples:")
for loc in localizedUsersDict:
    print("    " + loc + " " + demo.getGeoUnit(code=loc).label)
    for u in localizedUsersDict[loc][:10]:
        print("        " + u[0] + " " + f"'{u[1]}'")
