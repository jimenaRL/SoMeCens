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

from somecens.chile.conf import CHILEAGECATS, CHILEGENDERCATS
from somecens.us.conf import USAGECATS, USGENDERCATS
from somecens.nuts.conf import NUTS3AGECATS, NUTS3GENDERCATS

from somecens import DemoGraph
from somecens.tools import \
    parseFlatAgeDistributions, \
    getUnitsAliases, \
    getCountryAliases, \
    getOtherCountriesNames, \
    matchUsersLocations

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'

COUNTRYDATAPATH = os.path.join(DIRPATH, "data", "${country}")
GEOUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_geoUnits_nuts_2024.csv")
SUBUNITSPATH = os.path.join(COUNTRYDATAPATH, "${country}_subUnits_nuts_2024.yml")
GENDERDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_gender_distribution_nuts_2024.csv")
AGEDISTPATH = os.path.join(COUNTRYDATAPATH, "${country}_age_distribution_nuts_2024.csv")
USERSPATH = os.path.join(COUNTRYDATAPATH, "${country}_metadata_epo_${metadatayear}.csv")
# Create dict of relevant stop words per languages of country
DEFAULTSTOPWORDS = ""
EXPORTSFOLDER = os.path.join(DIRPATH, "results", "${date}", "${country}")
MYEARS = [2020, 2023, 2025]
EXPORTGEOUNITSPATH = os.path.join(EXPORTSFOLDER, f'units_nuts_2024.csv')
EXPORTSTATSPATH = os.path.join(EXPORTSFOLDER, 'nb_matchs_perc_${country}_nuts_2024_${level}.csv')
EXPORTUSERSPATH = os.path.join(EXPORTSFOLDER, 'localized_users_epo_${metadatayear}_nuts_2024.csv')
EXPORTFULLUSERSPATH = os.path.join(EXPORTSFOLDER, 'localized_users_full_epo_${metadatayear}_nuts_2024.csv')
EXPORTEXCELPATH = os.path.join(EXPORTSFOLDER, '${country}_units_users_reports_epo_${metadatayear}_nuts_2024.xlsx')


# 0. parse arguments and set paths
ap = ArgumentParser()

ap.add_argument('--country', type=str, required=True)
ap.add_argument('--metadatayear', type=int, required=True, choices=MYEARS)
ap.add_argument('--usersdatapath', type=str, default=USERSPATH)
ap.add_argument('--genderdistpath', type=str, default=GENDERDISTPATH)
ap.add_argument('--agedistpath', type=str, default=AGEDISTPATH)
ap.add_argument('--subunitspath', type=str, default=SUBUNITSPATH)
ap.add_argument('--unitspath', type=str, default=GEOUNITSPATH)
ap.add_argument('--stopwords', type=str, default=DEFAULTSTOPWORDS)
ap.add_argument('--nbuserdump', type=int, default=1000)
ap.add_argument('--exportsfolder', type=str, default=EXPORTSFOLDER)
ap.add_argument('--ignoreErrors', action="store_false")
ap.add_argument('--unitsexportpath', type=str, default=EXPORTGEOUNITSPATH)
ap.add_argument('--statsexportpath', type=str, default=EXPORTSTATSPATH)
ap.add_argument('--usersexportpath', type=str, default=EXPORTUSERSPATH)
ap.add_argument('--fullusersexportpath', type=str, default=EXPORTFULLUSERSPATH)
ap.add_argument('--excelexportpath', type=str, default=EXPORTEXCELPATH)

date = datetime.today().strftime('%Y%m%d')

args = ap.parse_args()
country = args.country
metadatayear = args.metadatayear
usersdatapath = Template(args.usersdatapath).safe_substitute(country=country, metadatayear=metadatayear)
genderdistpath = Template(args.genderdistpath).safe_substitute(country=country)
agedistpath = Template(args.agedistpath).safe_substitute(country=country)
subunitspath = Template(args.subunitspath).safe_substitute(country=country)
unitspath = Template(args.unitspath).safe_substitute(country=country)
stopwords =  args.stopwords.split("|")
nbuserdump = args.nbuserdump
ignoreErrors = args.ignoreErrors
statsexportpath = Template(args.statsexportpath).safe_substitute(country=country, date=date)
unitsexportpath = Template(args.unitsexportpath).safe_substitute(country=country, date=date)
usersexportpath = Template(args.usersexportpath).safe_substitute(country=country, date=date)
fullusersexportpath = Template(args.fullusersexportpath).safe_substitute(country=country, date=date)
excelexportpath = oTemplate(args.excelexportpath).safe_substitute(country=country, date=date)

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

#  0. Set options
if country == 'us':
    encoding = "ISO-8859-1"
    gendercategories = USGENDERCATS
    agecategories = USAGECATS
elif country == 'chile':
    encoding = "utf-8"
    gendercategories = CHILEGENDERCATS
    agecategories = CHILEAGECATS
else: # nuts countries
    gendercategories = NUTS3GENDERCATS
    agecategories = NUTS3AGECATS
    encoding = "utf-8"

#  1. Load sociodemographic data
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
        ageDist = [r for r in csv.DictReader(f)]
    print(f"Csv age distribution file loaded from {agedistpath}")
else:
    ageDist = []

ageDist = parseFlatAgeDistributions(ageDist)

with open(usersdatapath, 'r') as f:
    metadata = [r for r in csv.reader(f)]
print(f"Locations file with {len(metadata)} entries loaded from {agedistpath}")

# 2. Create demograp object and set:
#   - age distribution per geographical unit
#   - gender distributions per geographical unit
#   - subunits (LAUS)

raiseErrors = not ignoreErrors

demo = DemoGraph(
    demography=geoUnits,
    ageCats=agecategories,
    genderCats=gendercategories)
if subUnits:
    demo.setSubUnitsNames(subUnits)
if genderDist:
    demo.setGenderDistributions(genderDist)
if ageDist:
    demo.setAgeDistributions(ageDist, raiseErrors=raiseErrors, verbose=True)

# show
demo.showGeoUnits(max_level=0)

# 2. Match locations users from metadata and add information to demograph
other_countries = getOtherCountriesNames(country)
banned_words = other_countries - {"luxembourg"}

aliases = {demo.countryCode: getCountryAliases(country)}
aliases.update(getUnitsAliases(country))

match_kwargs = {
    "stopwords": stopwords,
    "split_characters": ["-", "/", "|", ".", "'", "(", ")"],
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

# 4. make exports

# 4.O export flatten units
unitReport, unitsColumns = demo.exportUnitsReport(unitssavepath)
os.system(f"xan v {unitssavepath}")

# 4.1 export matchs stats per level for cloropleths visualizations
for level in range(demo.getDeepestLevel() + 1) :
    path = Template(statsexportpath).safe_substitute(level=level)
    demo.exportLocalizationsMatchesPerc(level, path, descendants=True, add_headers=False)
    os.system(f"xan v --no-headers {path}")

# 4.2 export localized users
localizedUsers, localizedUsersColumns = demo.exportLocalizedUsers(
    usersexportpath,
    full_path=fullusersexportpath)
os.system(f"xan v {usersexportpath}")
os.system(f"xan v {fullusersexportpath}")

with pd.ExcelWriter(excelexportpath) as writer:

    unitsColumns = [" ".join(c.split("_")) for c in unitsColumns]
    pd.DataFrame(data=unitReport, columns=unitsColumns) \
        .to_excel(writer, index=False, sheet_name=f"units stats")

    localizedUsersColumns = [" ".join(c.split("_")) for c in localizedUsersColumns]
    df = pd.DataFrame(data=localizedUsers, columns=localizedUsersColumns)
    df = df.sample(n=min(len(df), 10000), random_state=84)
    try:
        df.to_excel(writer, index=False, sheet_name=f"localized users")
    except:
        df['location'] = df['location'].apply(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        df.to_excel(writer, index=False, sheet_name=f"localized users")

print(f"Excel report wrote at {excelexportpath}")

# 4. Make choropleth with:
#   - number of matched users in each geographical unit
#   - proportion of matched users per geographical unit

# For EU use https://gisco-services.ec.europa.eu/image/
# For USA see the us_cloropleth.py script in this same folder
