# =============================================================================
# Script to standardize NUTS data to Geodemograph inputs:
#
#    - Load metadata using auxiliar methods to request epo databases
#    - Load distributions and subunits using auxiliar methods to parse NUTS data
#    - Save jsonl, yaml and csv files
# =============================================================================

import os
import csv
import yaml
import json
from string import Template
from argparse import ArgumentParser

from somecens.epo.tools import getMetadata
from somecens.nuts.tools import \
    getLaus, \
    getUnits, \
    getNutsAgeDistributions, \
    getNutsGenderDistributions

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
DATAPATH = os.path.join(DIRPATH, "data")
DEFAULTEPODBPATH = os.path.join(
    DATAPATH,
    "${country}",
    "${country}_${metadatayear}_pseudonymized_alldata.db")
DEFAULTOUTFOLDER = os.path.join(DATAPATH, "${country}")
DEFAULTNUTSYEAR = 2024

# parse arguments and set paths
ap = ArgumentParser()
ap.add_argument('--country', type=str, required=True)
ap.add_argument('--metadatayear', type=int, required=False)
ap.add_argument('--epodbpath', type=str, default=DEFAULTEPODBPATH)
ap.add_argument('--nutsyear', type=int, default=DEFAULTNUTSYEAR)
ap.add_argument('--outfolder', type=str, default=DEFAULTOUTFOLDER)

args = ap.parse_args()
country = args.country
metadatayear = args.metadatayear
nutsyear = args.nutsyear
epodbpath = args.epodbpath
outfolder = args.outfolder
nutsyear = args.nutsyear

epodbpath = Template(epodbpath).safe_substitute(
    country=country,
    metadatayear=metadatayear)

outfolder = Template(outfolder).safe_substitute(country=country)
os.makedirs(outfolder, exist_ok=True)

params = vars(args)
params.update({
    "epodbpath" : epodbpath,
    "outfolder" : outfolder
})
print("---------------------------------------------------------")
print(f"PARAMETERS:\n{yaml.dump(params)}")
print("---------------------------------------------------------")

# load metadata using auxiliar methods to request epo databases
columns = ['pseudo_id', 'location', 'screen_name']
metadata = getMetadata(epodbpath, columns=columns, not_null_column="location")

# load distributions and subunits using auxiliar methods to parse NUTS data
geoUnits = getUnits(country=country,  year=nutsyear)
subUnits = getLaus(country=country)
genderDist = getNutsGenderDistributions(country=country, year=nutsyear)
ageDist = getNutsAgeDistributions(country=country, year=nutsyear)

# exports
metadatapath = os.path.join(outfolder, f"{country}_metadata{metadatayear}.csv")
with open(metadatapath, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(metadata)
print(f"Csv metadata file saved at {metadatapath}")

unitspath = os.path.join(outfolder, f"france_geoUnits_nuts{nutsyear}.csv")
columns = geoUnits[0].keys()
unitsdata = [g.values() for g in geoUnits]
with open(unitspath, "w") as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(unitsdata)
print(f"Csv file with {country} geographical units saved at {unitspath}")

subunitspath = os.path.join(outfolder, "france_subUnits.yml")
with open(subunitspath, "w") as f:
   yaml.dump(subUnits, f)
print(f"Yaml file with {country} geographical geounits saved at {subunitspath}")

genderdistname = os.path.join(
    outfolder,
    f"france_gender_distribution_nuts{nutsyear}")
with open(genderdistname + '.jsonl', "w") as f:
    f.writelines([json.dumps(l)+'\n' for l in genderDist])
print(f"Jsonl gender distribution file saved at {genderdistname}.jsonl")

with open(genderdistname + '.csv', 'w', newline='') as csvfile:
    fieldnames = genderDist[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for d in genderDist:
        writer.writerow(d)
print(f"Csv gender distribution file saved at {genderdistname}.csv")

agedistname = os.path.join(
    outfolder,
    f"france_age_distribution_nuts{nutsyear}")
with open(agedistname + ".jsonl", "w") as f:
    f.writelines([json.dumps(l)+'\n' for l in ageDist])
print(f"Jsonl age distribution file saved at {agedistname}.jsonl")

with open(agedistname + '.csv', 'w', newline='') as csvfile:
    fieldnames = ageDist[0].keys()
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for d in ageDist:
        writer.writerow(d)
print(f"Csv age distribution file saved at {agedistname}.csv")
