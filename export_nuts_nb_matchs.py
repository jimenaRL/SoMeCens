from glob import glob
from somecens.nuts.tools import getUnits
from somecens.nuts.conf  import COUNTRYCODES
from somecens.epo.tools import getMetadata
from somecens.demograph import DemoGraph
from somecens.tools import matchUsersLocations

nuts_year = 2024
metadata_year = 2023

for country in COUNTRYCODES.keys():

    print(f"----- {country} nuts_{nuts_year} metadata_{metadata_year} -----")

    # get last release
    dbpathpattern = f"/mnt/hdd2/epodata/stage/*/pseudonymized_alldata/{country}_{metadata_year}_pseudonymized_alldata.db"
    candidates = glob(dbpathpattern)
    candidates.sort()
    if len(candidates) == 0:
        print(f"No db found for country at {dbpath}")
        continue
    dbpath = candidates[-1]
    print(f"Last db release fund at {dbpathpattern}")

    geo_units = getUnits(country, year=nuts_year)
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
