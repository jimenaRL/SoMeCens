# =============================================================================
# Script to create a Demograph object representing a country in order to:
#
#   1. get organized sociodemographic information
#   2. localize user with geographic subdivisions
#   3. create choropleth maps to show sociodemographic and localisation infos
# =============================================================================

from somecens import DemoGraph

DATADIR = "TO ADD"
COUNTRY = "france"

with open(os.path.join(DATADIR, COUNTRY, f"{COUNTRY}_geounits.yml")) as f:
    geoUnits = yaml.safe_load(f)

with open(os.path.join(DATADIR, COUNTRY, f"{COUNTRY}_gender_dist.yml")) as f:
    genderDist = yaml.safe_load(f)

with open(os.path.join(DATADIR, COUNTRY, f"{COUNTRY}e_age_dist.yml")) as f:
    ageDist = yaml.safe_load(f)

with open(os.path.join(DATADIR, COUNTRY, f"{COUNTRY}_subunits.yml")) as f:
    subUnits = yaml.safe_load(f)

with open(os.path.join(DATADIR, f"{COUNTRY}_metadata.csv")) as f:
    metadata = [r for r in csv.reader(f)]

# 1. Create demograp object and set:
#   - age distribution per geographical unit
#   - gender distributions per geographical unit
#   - subunits (LAUS)

demo = DemoGraph(demography=geoUnits)
demo.setGenderDistributions(genderDist)
demo.setAgeDistributions(ageDist)
demo.setSubUnitsNames(subUnits)

# show
demo.showGeoUnits(max_level=0)


# 2. Match locations users from metadata and add information to demograph

geounits_locations = demo.getSubUnits()

match_kwargs = {
    "stopwords": "SET STOP WORDS FROM FRENCH HERE",
    "split_characters": ["-"],
    "search_index": 1,
    "has_headers": True
}

banned_words = "SET ALL COUNTRIES HERE"

multiUsersLocs = matchUsersLocations(
    locations=geounits_locations,
    data=metadata,
    banned_words=banned_words,
    **match_kwargs)

demo.setUsersLocations(multiUsersLocs)


# 3. Export matched locations to csv


# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit
