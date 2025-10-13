# =============================================================================
# Script to create a Demograph object representing France in order to:
#
#   1. Load sociodemographic information
#   2. Localize user with geographic subdivisions
#   3.  reate choropleth maps to show sociodemographic and localisation infos
# =============================================================================

import os
import csv
import yaml
import json
import time
from string import Template
from argparse import ArgumentParser

import emoji
from random import randint

from somecens import DemoGraph
from somecens.tools import matchUsersLocations
from somecens.epo.tools import getMetadata
from somecens.nuts.tools import \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
SMCDATAPATH = os.path.join(DIRPATH, "somecens", "data")

COUNTRYDATAPATH = os.path.join(DIRPATH, "data", "${country}")
GEOUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_geoUnits_nuts2024.yml")
SUBUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_subUnits.yml")
GENDERDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_gender_distribution_nuts2024.jsonl")
AGEDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_age_distribution_nuts2024.jsonl")
USERSPATH = os.path.join(COUNTRYDATAPATH, "${country}_metadata2020.csv")

# 0. parse arguments and set paths
ap = ArgumentParser()

ap.add_argument('--country', type=str, required=True)
ap.add_argument('--usersdatapath', type=str, default=USERSPATH)
ap.add_argument('--genderdistpath', type=str, default=GENDERDISTPATH)
ap.add_argument('--agedistpath', type=str, default=AGEDISTPATH)
ap.add_argument('--subunitspath', type=str, default=SUBUNITSPATH)
ap.add_argument('--unitspath', type=str, default=GEOUNITSPATH)
ap.add_argument('--limit', type=int, default=0)
ap.add_argument('--random', type=bool, default=False)
ap.add_argument('--debugcode', type=str, default='')

args = ap.parse_args()
country = args.country
usersdatapath = Template(args.usersdatapath).safe_substitute(country=country)
genderdistpath = Template(args.genderdistpath).safe_substitute(country=country)
agedistpath = Template(args.agedistpath).safe_substitute(country=country)
subunitspath = Template(args.subunitspath).safe_substitute(country=country)
unitspath = Template(args.unitspath).safe_substitute(country=country)
limit = args.limit
random = args.random
debugcode = args.debugcode

params = vars(args)
params.update({
    "usersdatapath" : usersdatapath,
    "genderdistpath" : genderdistpath,
    "agedistpath" : agedistpath,
    "subunitspath" : subunitspath,
    "unitspath": unitspath
    })
print("---------------------------------------------------------")
print(f"PARAMETERS:\n{yaml.dump(params)}")
print("---------------------------------------------------------")

with open(os.path.join(SMCDATAPATH, "pays_capitales.csv")) as f:
    pays = {d["country"] for d in csv.DictReader(f)}

with open(os.path.join(SMCDATAPATH, "geocodes_countries_capitals.csv")) as f:
    countries = {d["Country"] for d in csv.DictReader(f)}

#  1. Load sociodemographic data

with open(unitspath, "r") as f:
   geoUnits = yaml.safe_load(f)
print(f"Geographical units load from {unitspath}")

with open(subunitspath, "r") as f:
   subUnits = yaml.safe_load(f)
print(f"Geographical subunits load from {subunitspath}")

with open(genderdistpath, "r") as f:
    genderDist = [json.loads(l) for l in f.readlines()]
print(f"Jsonl gender distribution load from {genderdistpath}")

with open(agedistpath, "r") as f:
    ageDist = [json.loads(l) for l in f.readlines()]
print(f"Jsonl age distribution file load from {agedistpath}")

with open(usersdatapath, 'r') as f:
    metadata = [r for r in csv.reader(f)]
print(f"Locations file with {len(metadata)} entries load from {agedistpath}")
if limit:
    metadata = metadata[:limit]

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
match_kwargs = {
    "stopwords": ["le", "la", "de", "en", "au"],
    "split_characters": ["-", "/", "|"],
    "search_index": 1,
    "has_headers": True,
    "verbose": True
}

with open('somecens/data/flags_unicode_emoji.json', 'r') as f:
    flags_unicode_emojis = json.load(f)
with open("somecens/data/franceFlags.txt", 'r') as f:
    french_flag_emojis = [d['name'] for d in csv.DictReader(f)]

banned_emojis = list(flags_unicode_emojis.values())
for f in french_flag_emojis:
    banned_emojis.remove(f)

banned_words = countries.union(pays)
banned_words.remove('France')
banned_words = banned_words.union({"Québec"})
locations = demo.getAllSubUnits()

# /!\ MEASURE TIME /!\
start = time.time()
users_matched_locations = matchUsersLocations(
    locations=locations,
    data=metadata,
    banned_words=banned_words,
    allowed_emojis=french_flag_emojis,
    banned_emojis=banned_emojis,
    **match_kwargs)

demo.setUsersLocations(users_matched_locations)

# show
if not debugcode:
    rndIdx = randint(0, len(demo.locations))
    debugcode = list(demo.locations.keys())[rndIdx]

print(f"-------- {debugcode} {demo.locations[debugcode]} --------")
print(f"Subunits:")
print(demo.getSubUnits(debugcode))
print(f"Localized users:")
for loc, usr in demo.getLocalizedUsers(code=debugcode, descendants=True).items():
    print("    " + loc + " " + demo.getGeoUnit(code=loc).label)
    for u in usr:
        print("            " + u[0] + " " + f"'{u[1]}'")

duration = time.time() - start
print(f"Matching {len(metadata)} users locations took {duration} seconds.")

# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit


# CHECK https://python-graph-gallery.com/choropleth-map-plotly-python/