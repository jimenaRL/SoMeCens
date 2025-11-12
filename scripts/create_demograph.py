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
import pandas as pd
from datetime import datetime

from string import Template
from argparse import ArgumentParser

import emoji
from random import randint, shuffle

import numpy as np

from somecens import DemoGraph
from somecens.tools import \
    getAliases, \
    getOtherCountriesNames, \
    matchUsersLocations
from somecens.epo.tools import getMetadata
from somecens.nuts.tools import \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'

COUNTRYDATAPATH = os.path.join(DIRPATH, "data", "${country}")
GEOUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_geoUnits_nuts2024.csv")
SUBUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_subUnits.yml")
GENDERDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_gender_distribution_nuts2024.csv")
AGEDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_age_distribution_nuts2024.jsonl")
USERSPATH = os.path.join(COUNTRYDATAPATH, "${country}_metadata2023.csv")
# Create dict of relevant stop words per languages of country
DEFAULTSTOPWORDS = ""
EXPORTSFOLDER = os.path.join(DIRPATH, "results", "${date}")

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
ap.add_argument('--nbuserdump', type=int, default=1000)
ap.add_argument('--exportsfolder', type=str, default=EXPORTSFOLDER)

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
nbuserdump = args.nbuserdump
exportsfolder = Template(args.exportsfolder).safe_substitute(date=datetime.today().strftime('%Y%m%d'))
exportsfoldercountry = os.path.join(exportsfolder, country)
os.makedirs(exportsfolder, exist_ok=True)
os.makedirs(exportsfoldercountry, exist_ok=True)

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


#  1. Load sociodemographic data

if country == 'United States':
    encoding = "ISO-8859-1"
else:
    encoding = "utf-8"
with open(unitspath, "r", encoding=encoding) as f:
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
other_countries = getOtherCountriesNames(country)
banned_words = other_countries

print("nederland" in banned_words)

import pdb; pdb.set_trace()  # breakpoint b659d0a8 //

aliases = {'BE': getAliases(country)}

match_kwargs = {
    "stopwords": stopwords,
    "split_characters": ["-", "/", "|", ".", "'"],
    "search_index": [1],
    "has_headers": True,
}

locations = demo.getAllSubUnits(max_level=3)

start = time.time()
users_matched_locations = matchUsersLocations(
    locations=locations,
    data=metadata,
    aliases=aliases,
    banned_words=banned_words,
    verbose=False,
    **match_kwargs)

duration = time.time() - start
print(f"Whole matching {len(metadata)} users locations took {duration} seconds.")

demo.setUsersLocations(users_matched_locations)

# 3. show
if not debugcode:
    rndIdx = randint(0, len(demo.locations))
    debugcode = list(demo.locations.keys())[rndIdx]

debuglabel = demo.getGeoUnit(code=debugcode).label

# print(f"-------- {debugcode} {demo.locations[debugcode]} --------")
# print(f"Descendants:")
# print([gg.label for gg in demo.getDescendants(demo.getGeoUnit(debugcode))])
# print(f"Localized users sample:")
# users_dict = demo.getLocalizedUsers(code=debugcode, descendants=True)

# 4. make exports

# 4.O export flatten units
path = os.path.join(exportsfoldercountry, f'units.csv')
demo.exportUnits(path)

# 4.1 export localized users
path = os.path.join(exportsfoldercountry, f'localized_users.csv')
localizedUsers = demo.exportLocalizedUsers(path)

# 4.2 export matchs stats for eu  cloropleths
for level in range(demo.getDeepestLevel() + 1) :
    path = os.path.join(exportsfoldercountry, f'nb_matchs_{country.replace(' ', '')}_nuts_{level}.csv')
    demo.exportLocalizationsMatches(level, path, descendants=True, add_headers=False)
    os.system(f"xan head {path} | xan v")
    path = os.path.join(exportsfoldercountry, f'nb_matchs_perc_{country.replace(' ', '')}_nuts_{level}.csv')
    demo.exportLocalizationsMatchesPerc(level, path)
    os.system(f"xan head {path} | xan v")

# 4.3 export excel for debugging
excelfile = os.path.join(exportsfolder, f'localized_users_{country.replace(' ', '')}.xlsx')
with pd.ExcelWriter(excelfile) as writer:

    # export matchs per unit
    data = []
    statsHeaders = [
        'level',
        'code',
        'label',
        'unit population',
        'matched users',
        'total matched users (with descendant)',
        'total matched users percent (with descendant)',
        'subunits'
    ]

    for g in demo.geoUnits:
        stats = demo.getGeoUnitLocalizationsStats(g.code)
        subunits = demo.getSubUnits(g.code)
        stats.append(' | '.join(subunits))
        data.append(stats)

    predata = [["NUTS level", "mean matched %", "median matched %", "mean pop.", "median pop.", "", "", ""]]
    for l in range(demo.getDeepestLevel() + 1):
        mean_perc = np.mean([d[6] for d in data if d[0]==l])
        median_perc = np.median([d[6] for d in data if d[0]==l])
        mean_pop = np.mean([d[3] for d in data if d[0]==l])
        median_pop = np.median([d[3] for d in data if d[0]==l])
        predata.append([str(l), f"{mean_perc:.2f}", f"{median_perc:.2f}", f"{mean_pop:.0f}", f"{median_pop:.0f}", "", "", ""])
    predata.append(["", "", "", "", "", "", "", ""])
    predata.append(["", "", "", "", "", "", "", ""])

    predata.append(statsHeaders)

    df = pd.DataFrame(data=predata+data)
    df.to_excel(writer, index=False, sheet_name=f"statistics")

    # export users matchs
    columns = ["pseudo_id", "location", "screen_name", "normalized_location"]
    for g in demo.geoUnits:
        users = demo.getLocalizedUsers(code=g.code, descendants=False)[g.code]
        stats = demo.getGeoUnitLocalizationsStats(g.code)

        predata = [
            ["Level", g.level, "", ""],
            ["Code", g.code, "", ""],
            ["Label", g.label, "", ""],
            ["Population", stats[3], "", ""],
            ["Matchs", stats[4], "", ""],
            ["Subunits", ' | '.join(demo.getSubUnits(g.code)), "", ""],
            ["", "", "", ""],
        ]
        predata.append(columns)
        df = pd.DataFrame(data=predata+users)
        df = df.drop(df.columns[2], axis=1)
        df = df.iloc[:nbuserdump]
        df = df.map(
                lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        df.to_excel(writer, index=False, sheet_name=f"{g.code}")

print(f"Mathch file save at {excelfile}")
# os.system(f"open {excelfile}")


# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit

# For EU use https://gisco-services.ec.europa.eu/image/
# For USA see script in the same folder
