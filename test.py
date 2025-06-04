from somecens import DemoGraph
from somecens.nuts.tools import \
    getUnits, getNutsLocations, getNutsLocationsLevel, getNutsGenderDistributions, getNutsAgeDistributions
from somecens.epo.tools import getMetadata
from somecens.tools import matchUsersLocations

year = 2024
country = 'france'
print(f"---------------- {country} {year}----------------")

locs_level2_2024 = getNutsLocationsLevel(country, level=2, year=year)
locations = getNutsLocations(country, format='flatten', year=year)
geo_units =   getUnits(country, year=year)

demo = DemoGraph(demography=geo_units)
# demo.showGeoUnits()

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
demo.showGeoUnits()

