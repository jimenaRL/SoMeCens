import os
import yaml

DIRPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDERPATH =  os.path.join(DIRPATH, 'data')

EPOFILES = {
    'epo_country_years_in_nuts': 'epo_country_years_in_nuts.yml'
}

EPOYEARSPATH = os.path.join(DATAFOLDERPATH, EPOFILES['epo_country_years_in_nuts'])

with open(EPOYEARSPATH, "r") as fh:
    COUNTRYEARS = yaml.load(fh, Loader=yaml.SafeLoader)

METADATAFIELDS = ['screen_name', 'description', 'location']
METADATATABLE = "metadata"

DEFAULTDB = "pseudonymized_alldata"
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"


