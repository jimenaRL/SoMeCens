import os
import yaml

DIRPATH = os.path.dirname(os.path.realpath(__file__))

NUTSPATH = os.path.join(DIRPATH, 'data/nuts.csv')

NUTSCODESPATH = os.path.join(DIRPATH, 'data/nuts_codes_country.yml')
EPOYEARSPATH = os.path.join(DIRPATH, 'data/epo_country_years_in_nuts.yml')

with open(NUTSCODESPATH, "r") as fh:
    CODESCOUNTRY = yaml.load(fh, Loader=yaml.SafeLoader)
COUNTRYCODES = {v: k for k,v in CODESCOUNTRY.items()}

with open(EPOYEARSPATH, "r") as fh:
    COUNTRYEARS = yaml.load(fh, Loader=yaml.SafeLoader)

DEFAULTDB = "pseudonymized_alldata"
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"

NUTSLEVELS = [1, 2, 3]

METADATAFIELDS = ['screen_name', 'description', 'location']
METADATATABLE = "metadata"


