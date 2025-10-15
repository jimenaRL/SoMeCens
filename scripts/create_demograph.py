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
from random import randint, shuffle

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
GEOUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_geoUnits_nuts2024.csv")
SUBUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_subUnits.yml")
GENDERDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_gender_distribution_nuts2024.csv")
AGEDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_age_distribution_nuts2024.jsonl")
USERSPATH = os.path.join(COUNTRYDATAPATH, "${country}_metadata2020.csv")
DEFAULTSTOPWORDS = "le|la|de|en|au"

# 0. parse arguments and set paths
ap = ArgumentParser()

ap.add_argument('--country', type=str, required=True)
ap.add_argument('--usersdatapath', type=str, default=USERSPATH)
ap.add_argument('--genderdistpath', type=str, default=GENDERDISTPATH)
ap.add_argument('--agedistpath', type=str, default=AGEDISTPATH)
ap.add_argument('--subunitspath', type=str, default=SUBUNITSPATH)
ap.add_argument('--unitspath', type=str, default=GEOUNITSPATH)
ap.add_argument('--stopwords', type=str, default=DEFAULTSTOPWORDS)
ap.add_argument('--debuglimit', type=int, default=0)
ap.add_argument('--debugcode', type=str, default='')

args = ap.parse_args()
country = args.country
usersdatapath = Template(args.usersdatapath).safe_substitute(country=country)
genderdistpath = Template(args.genderdistpath).safe_substitute(country=country)
agedistpath = Template(args.agedistpath).safe_substitute(country=country)
subunitspath = Template(args.subunitspath).safe_substitute(country=country)
unitspath = Template(args.unitspath).safe_substitute(country=country)
stopwords =  args.stopwords.split("|")
debuglimit = args.debuglimit
debugcode = args.debugcode

params = vars(args)
params.update({
    "usersdatapath" : usersdatapath,
    "genderdistpath" : genderdistpath,
    "agedistpath" : agedistpath,
    "subunitspath" : subunitspath,
    "unitspath": unitspath,
    "stopwords": stopwords,
    })
print("---------------------------------------------------------")
print(f"PARAMETERS:\n{yaml.dump(params)}")
print("---------------------------------------------------------")


#  0. Load countries data

with open(os.path.join(SMCDATAPATH, "pays_capitales.csv")) as f:
    pays = {d["country"] for d in csv.DictReader(f)}

with open(os.path.join(SMCDATAPATH, "geocodes_countries_capitals.csv")) as f:
    countries = {d["Country"] for d in csv.DictReader(f)}

#  1. Load sociodemographic data

with open(unitspath, "r", encoding = "ISO-8859-1") as f:
    geoUnits = [r for r in csv.DictReader(f)]
print(f"Geographical units loaded from {unitspath}")

if subunitspath:
    with open(subunitspath, "r") as f:
       subUnits = yaml.safe_load(f)
    print(f"Geographical subunits loaded from {subunitspath}")
else:
    subUnits = {}

if genderdistpath:
    with open(genderdistpath, "r") as f:
        genderDist = [r for r in csv.DictReader(f)]
    print(f"Csv file with gender distributions loaded from {genderdistpath}")
else:
    genderDist = []

if agedistpath:
    with open(agedistpath, "r") as f:
        ageDist = [json.loads(l) for l in f.readlines()]
    print(f"Jsonl age distribution file loaded from {agedistpath}")
else:
    ageDist = []

with open(usersdatapath, 'r') as f:
    if debuglimit:
        metadata = [r for r,_ in zip(csv.reader(f), range(debuglimit))]
    else:
        metadata = [r for r in csv.reader(f)]
print(f"Locations file with {len(metadata)} entries loaded from {agedistpath}")

# 2. Create demograp object and set:
#   - age distribution per geographical unit
#   - gender distributions per geographical unit
#   - subunits (LAUS)

demo = DemoGraph(demography=geoUnits)
if subUnits:
    demo.setSubUnitsNames(subUnits)
if genderDist:
    demo.setGenderDistributions(genderDist)
if ageDist:
    demo.setAgeDistributions(ageDist)

# show
demo.showGeoUnits(max_level=0)

# 2. Match locations users from metadata and add information to demograph
match_kwargs = {
    "stopwords": stopwords,
    "split_characters": ["-", "/", "|"],
    "search_index": 1,
    "has_headers": True,
}

# with open('somecens/data/flags_unicode_emoji.json', 'r') as f:
#     flags_unicode_emojis = json.load(f)
# with open("somecens/data/franceFlags.txt", 'r') as f:
#     french_flag_emojis = [d['name'] for d in csv.DictReader(f)]

# banned_emojis = list(flags_unicode_emojis.values())
# for f in french_flag_emojis:
#     banned_emojis.remove(f)

banned_words = countries.union(pays)
# TO DO: make file with of aliases and translations per country
if country == 'france':
    banned_words.remove('France')

if country == 'us':
    banned_words.remove('États-Unis')
    banned_words.remove('United States')
    banned_words.remove('United States Minor Outlying Islands')

locations = demo.getAllSubUnits(max_level=3)
# print(f"LOCATIONS ARE:\n{yaml.dump(locations)}")

start = time.time()
users_matched_locations = matchUsersLocations(
    locations=locations,
    data=metadata,
    banned_words=banned_words,
    # allowed_emojis=french_flag_emojis,
    # banned_emojis=banned_emojis,
    verbose=True,
    **match_kwargs)

duration = time.time() - start
print(f"Whole matching {len(metadata)} users locations took {duration} seconds.")

demo.setUsersLocations(users_matched_locations)

# show
if not debugcode:
    rndIdx = randint(0, len(demo.locations))
    debugcode = list(demo.locations.keys())[rndIdx]

print(f"-------- {debugcode} {demo.locations[debugcode]} --------")
print(f"Localized users sample:")
for loc, usr in demo.getLocalizedUsers(code=debugcode, descendants=True).items():
    print(f"    {loc} {demo.getGeoUnit(code=loc).label} {len(usr)} matchs")
    shuffle(usr)
    for u in usr[:30]:
        print("            " + u[0] + " " + f"'{u[1]}'")
print(f"Subunits:")
print(demo.getSubUnits(debugcode))

# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit


# CHECK https://python-graph-gallery.com/choropleth-map-plotly-python/
