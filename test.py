from somecens import DemoGraph
from somecens.nuts.tools import \
    getUnits, getNutsLocations, getNutsLocationsLevel, getNutsGenderDistributions
from somecens.epo.tools import getMetadata


if __name__ == "__main__":

    year = 2024
    country = 'belgium'
    print(f"---------------- {country} {year}----------------")

    metadata = getMetadata(f'{country}_2020_pseudonymized_alldata.db')
    locs_level2_2024 = getNutsLocationsLevel(country, level=2, year=year)
    locations = getNutsLocations(country, format='flatten', year=year)
    geo_units =   getUnits(country, year=year)


    demo = DemoGraph(demography=geo_units)
    demo.showGeoUnits()

    genderDist = getNutsGenderDistributions(country, year=year)
    demo.setGenderDistributions(genderDist)
    demo.showGeoUnits()
