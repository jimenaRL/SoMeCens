import yaml

with open('nuts_codes_country.yml', "r") as fh:
    CODESCOUNTRY = yaml.load(fh, Loader=yaml.SafeLoader)
COUNTRYCODES = {v: k for k,v in CODESCOUNTRY.items()}

with open('epo_country_years_in_nuts.yml', "r") as fh:
    COUNTRYEARS = yaml.load(fh, Loader=yaml.SafeLoader)

DEFAULTDB = "pseudonymized_alldata"
DEFAULTDBPATTERN = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"

NUTSLEVELS = [1, 2, 3]

METADATAFIELDS = ['screen_name', 'description', 'location']
METADATATABLE = "metadata"


