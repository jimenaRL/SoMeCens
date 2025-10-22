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
from datetime import datetime

from string import Template
from argparse import ArgumentParser

import emoji
from random import randint, shuffle

import numpy as np

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
USERSPATH = os.path.join(COUNTRYDATAPATH, "${country}_metadata2023.csv")
# Create dict of relevant stop words per languages of country
DEFAULTSTOPWORDS = ""
EXPORTSFOLDER = os.path.join(DIRPATH, "results", "${date}", "${country}")

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
exportsfolder = Template(args.exportsfolder).safe_substitute(
    country=country.replace(' ', ''), date=datetime.today().strftime('%Y%m%d'))
os.makedirs(exportsfolder, exist_ok=True)


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
match_kwargs = {
    "stopwords": stopwords,
    "split_characters": ["-", "/", "|", ".", "'"],
    "search_index": [1],
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

if country == 'netherlands':
    banned_words.remove("Pays-Bas")
    banned_words.remove("The Netherlands")

if country == 'luxembourg':
    banned_words.remove("Luxembourg")

if country == 'spain':
    banned_words.remove("Spain")
    banned_words.remove("Espagne")

if country == 'germany':
    banned_words.remove("Germany")
    banned_words.remove("Allemagne")

if country == 'italy':
    banned_words.remove("Italy")
    banned_words.remove("Italie")

if country == 'austria':
    banned_words.remove("Austria")

if country == 'czechia':
    banned_words.remove("Czechia")
    banned_words.remove("République tchèque")

if country == 'denmark':
    banned_words.remove("Denmark")
    banned_words.remove("Danemark")

if country == 'estonia':
    banned_words.remove("Estonia")
    banned_words.remove("Estonie")

if country == 'ireland':
    banned_words.remove("Ireland")
    banned_words.remove("Irlande")

if country == 'greece':
    banned_words.remove("Greece")
    banned_words.remove("Grèce")

if country == 'croatia':
    banned_words.remove("Croatia")
    banned_words.remove("Croatie")

if country == 'cyprus':
    banned_words.remove("Cyprus")
    banned_words.remove("Chypre")

if country == 'latvia':
    banned_words.remove("Latvia")
    banned_words.remove("Lettonie")

if country == 'lithuania':
    banned_words.remove("Lithuania")
    banned_words.remove("Lituanie")

if country == 'hungary':
    banned_words.remove("Hungary")
    banned_words.remove("Hongrie")

if country == 'malta':
    banned_words.remove("Malta")
    banned_words.remove("Malte")

if country == 'poland':
    banned_words.remove("Poland")
    banned_words.remove("Pologne")

if country == 'portugal':
    banned_words.remove("Portugal")

if country == 'romania':
    banned_words.remove("Romania")
    banned_words.remove("Roumanie")

if country == 'slovenia':
    banned_words.remove("Slovenia")
    banned_words.remove("Slovénie")

if country == 'slovakia':
    banned_words.remove("Slovakia")
    banned_words.remove("Slovaquie")

if country == 'finland':
    banned_words.remove("Finland")
    banned_words.remove("Finlande")

if country == 'sweden':
    banned_words.remove("Sweden")
    banned_words.remove("Suède")


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

# 3. load matched data Demograph object and make relevants exports
demo.setUsersLocations(users_matched_locations)

# 4. show
# if not debugcode:
#     rndIdx = randint(0, len(demo.locations))
#     debugcode = list(demo.locations.keys())[rndIdx]

# debuglabel = demo.getGeoUnit(code=debugcode).label

# print(f"-------- {debugcode} {demo.locations[debugcode]} --------")
# print(f"Descendants:")
# print([gg.label for gg in demo.getDescendants(demo.getGeoUnit(debugcode))])
# print(f"Localized users sample:")
# users_dict = demo.getLocalizedUsers(code=debugcode, descendants=True)
# for descendant, users in users_dict.items():
#     print(f"\t{descendant} {debuglabel} ")
#     print(f"\t\tMatchs number: {len(users)}")
#     print(f"\t\tSubunits: {','.join(demo.getSubUnits(descendant))}")
#     shuffle(users)
#     for u in users[:5]:
#         print(f"\t\t\t{u[0]} {u[1]}")

# 5. make exports

# export matchs stats for eu api cloropleths
for level in range(demo.getDeepestLevel() + 1) :
    path = os.path.join(exportsfolder, f'nb_matchs_{country.replace(' ', '')}_nuts_{level}.csv')
    demo.exportLocalizationsMatches(level, path, descendants=True, add_headers=False)
    os.system(f"xan head {path} | xan v")
    path = os.path.join(exportsfolder, f'nb_matchs_perc_{country.replace(' ', '')}_nuts_{level}.csv')
    demo.exportLocalizationsMatchesPerc(level, path)
    os.system(f"xan head {path} | xan v")


# export excel for debugging
import pandas as pd
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
os.system(f"open {excelfile}")


# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit

# For EU use https://gisco-services.ec.europa.eu/image/
# For USA see script in the same folder
