import os
import random
import tempfile
from string import Template
from argparse import ArgumentParser
from fog.tokenizers import FingerprintTokenizer

from somecens import DemoGraph
from somecens.nuts.tools import \
    getLaus, \
    getUnits
from somecens.epo.tools import getMetadata
from somecens.tools import writeCsv, searchOccurrences, makeRegex, regexMatchUsersLocations

DEFAULTYEAR = 2024
DEFAULTMETAYEAR = 2020
DEFAULTCOUNTRY = 'france'
# METADATADB = f'{country}_2020_pseudonymized_alldata.db'
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/20250416/pseudonymized_alldata/${country}_${metadata_year}_pseudonymized_alldata.db"

# ap = ArgumentParser (prog="Test script for some4dem")
# ap.add_argument('--country', required=False, type=str, default=DEFAULTCOUNTRY)
# ap.add_argument('--year', required=False, type=str, default=DEFAULTYEAR)
# ap.add_argument('--metadata_year', required=False, type=str, default=DEFAULTMETAYEAR)
# ap.add_argument('--dbpath', required=False, type=str, default=DEFAULTDBPATTERN)

# args = ap.parse_args()
# country = args.country
# year = args.year
# metadata_year = args.metadata_year
# dbpath = Template(args.dbpath).safe_substitute(
#     country=country,
#     metadata_year=metadata_year)

# print(f"----- {country} nuts_{year} metadata_{metadata_year} -----")


tokenizer = FingerprintTokenizer(stopwords=["le", "la", "de"])

country = DEFAULTCOUNTRY
year = DEFAULTYEAR
metadata_year = DEFAULTMETAYEAR
dbpath = Template("france_2023_pseudonymized_alldata.db").safe_substitute(
    country=country,
    metadata_year=metadata_year)

geo_units = getUnits(country, year=year)
locations = {g["code"]: g["label"] for g in geo_units}

labels = [d['label'] for d in geo_units]
laus = [x for xs in getLaus('france').values() for x in xs]

columns = ['pseudo_id', 'location']
metadata = getMetadata(dbpath, columns)
usersLocations = set([m[1] for m in metadata])


stopwords = ["le", "la", "de"]
out = regexMatchUsersLocations(locations, metadata, stopwords, search_index=1)


exit()



def makesUniques(list):
    ss = {'|'.join(t) for t in list}
    return [s.split('|') for s in ss]

def makeRows(terms):
    return [[term, ' '.join(tok)] for term, tok in zip(terms, map(tokenizer, terms))]

labelsRows = makeRows(labels)
lausRows = makeRows(laus)
ulRows = makeRows(usersLocations)

headers = ["term", "tokenized"]
writeCsv(file="toEraseLabels.csv", rows=labelsRows, headers=headers)
writeCsv(file="toEraseLaus.csv", rows=lausRows, headers=headers)
writeCsv(file="toEraseUserLocation.csv", rows=ulRows, headers=headers)

n = random.randint(0, len(labelsRows))
os.system(f"xan search --regex '\\b{labelsRows[n][1]}\\b' toEraseUserLocation.csv | xan v")
print(f"LABEL: {labelsRows[n][0]}")
print(f"TOKENIZED: {labelsRows[n][1]}")


n = random.randint(0, len(labelsRows))
lau = lausRows[n][1]
os.system(f"xan search --regex '\\b{lausRows[n][1]}\\b' toEraseUserLocation.csv | xan v")
print(f"LABEL: {lausRows[n][0]}")
print(f"TOKENIZED: {lausRows[n][1]}")
