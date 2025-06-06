import os
from somecens.nuts.tools import getUnits
from somecens.nuts.conf  import COUNTRYCODES
from somecens.epo.tools import getMetadata
from somecens.demograph import DemoGraph
from somecens.tools import matchUsersLocations

year = 2024
metadata_year = 2020

for country in COUNTRYCODES.keys():

    dbpath = f"/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/{country}_2020_pseudonymized_alldata.db"
    if not os.path.exists(dbpath):
        print(f"Missing db at {dbpath}")
        continue

    print(f"----- {country} nuts_{year} metadata_{metadata_year} -----")
    geo_units = getUnits(country, year=year)
    demo = DemoGraph(demography=geo_units)

    columns = ['pseudo_id', 'location']
    metadata = getMetadata(dbpath, columns)
    usersLocations = matchUsersLocations(demo.locations, metadata, columns)
    demo.setUsersLocations(usersLocations)

    for level in [1, 2, 3]:
        demo.exportLocaliationsMatches(
            path=f'nb_matchs_{country}_nuts_{level}.csv',
            level=level
        )
