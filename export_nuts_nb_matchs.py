from somecens import DemoGraph
from somecens.nuts.tools import getUnits
from somecens.nuts.conf  import COUNTRYCODES

year = 2024
metadata_year = 2020

for country in COUNTRYCODES.keys():
    print(f"----- {country} nuts_{year} metadata_{metadata_year} -----")
    geo_units = getUnits(country, year=year)
    demo = DemoGraph(demography=geo_units)

    columns = ['pseudo_id', 'location']
    metadata = getMetadata(f'{country}_2020_pseudonymized_alldata.db', columns)
    usersLocations = matchUsersLocations(demo.locations, metadata, columns)
    demo.setUsersLocations(usersLocations)

    localizedUsersDict = demo.getLocalizedUsers(code="FRK21")
    print("Localized users examples:")
    for loc in localizedUsersDict:
        print("    " + loc + " " + demo.getGeoUnit(code=loc).label)
        for u in localizedUsersDict[loc][:10]:
            print("        " + u[0] + " " + f"'{u[1]}'")
