from somecens import DemoGraph
from somecens.nuts.tools import \
    getUnits, getNutsLocations, getNutsLocationsLevel, getNutsGenderDistributions, getNutsAgeDistributions, COUNTRYCODES, getLaus
from somecens.epo.tools import getMetadata
from somecens.tools import matchUsersLocations, matchUsersMultipleLocations

year = 2024
country = 'france'
metadata_year = 2020
# METADATADB = f'{country}_2020_pseudonymized_alldata.db'
METADATADB = f"/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/{country}_{metadata_year}_pseudonymized_alldata.db"

print(f"----- {country} nuts_{year} metadata_{metadata_year} -----")


# locs_level2_2024 = getNutsLocationsLevel(country, level=2, year=year)
# locations = getNutsLocations(country, format='flatten', year=year)
geo_units = getUnits(country, year=year)
laus = getLaus('france')

demo = DemoGraph(demography=geo_units)
demo.setSubUnitsNames(laus)
# demo.getGeoUnit(code='FRF').indentPrint()
# demo.getGeoUnit(code='FR10').indentPrint()
# demo.getGeoUnit(code='FR102').indentPrint()

# code = "FRK21"
# label = "Ile-de-France"
# print(f"The label of the NUTS code '{code}' is: '{demo.findLabelFromCode(code)}'")
# print(f"The NUTS codes associated to the label '{label}' are: {demo.findCodesFromLabel(label)}")
# demo.showGeoUnits()

# getUnit = demo.getGeoUnit(code='FRJ')
# getUnit_descendants = demo.getDescendants(getUnit)

genderDist = getNutsGenderDistributions(country, year=year)
demo.setGenderDistributions(genderDist)
# demo.showGeoUnits()

ageDist = getNutsAgeDistributions(country, year=year)
demo.setAgeDistributions(ageDist)
#demo.showGeoUnits()

columns = ['pseudo_id', 'location']
metadata = getMetadata(METADATADB, columns)

usersLocations = matchUsersLocations(
     locations=demo.locations,
     metadata=metadata,
     headers=columns,
     search_col='location',
     method='regex'
)
demo.setUsersLocations(usersLocations)
localizedUsersDict = demo.getLocalizedUsers(code="FRK28", descendants=True)
print("Localized users number:")
for loc in localizedUsersDict:
     print("    " + loc + " " + demo.getGeoUnit(code=loc).label + " " + str(len(localizedUsersDict[loc])))
     for u in localizedUsersDict[loc][:3]:
         print("            " + u[0] + " " + f"'{u[1]}'")



demo = DemoGraph(demography=geo_units)
demo.setSubUnitsNames(laus)
lausUsersLocations = matchUsersMultipleLocations(
    locations_groups=demo.getSubUnits(),
    metadata=metadata,
    headers=columns,
    search_col='location',
    method='regex'
)
demo.setUsersLocations(lausUsersLocations)
localizedUsersDictMulti = demo.getLocalizedUsers(code="FRK28", descendants=True)
print("Localized users number:")
for loc in localizedUsersDictMulti:
    print("    " + loc + " " + demo.getGeoUnit(code=loc).label + " " + str(len(localizedUsersDictMulti[loc])))
    for u in localizedUsersDictMulti[loc][:3]:
        print("            " + u[0] + " " + f"'{u[1]}'")


geo_units = demo.geoUnits
for g in geo_units:
    print(f"code: {g.code} | label: {g.label} | users found: {len(lausUsersLocations[g.code])}")


#for level in [1, 2, 3]:
#    demo.exportLocalizationsMatches(
#        path=f'nb_matchs_{country}_nuts_{level}.csv',
#        level=level
#    )


