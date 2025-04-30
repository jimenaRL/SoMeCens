import os
import yaml

DIRPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDERPATH =  os.path.join(DIRPATH, 'data')

NUTSLEVELS = [1, 2, 3]

NUTSFILES = {
    'nuts1': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2024.csv',
    'statistical_regions': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Statistical Regions.csv',
    'nutsAllLevels': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2021- NUTS2024.csv',
    'nutsCyrillicGreekLatin': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Cyrillic & Greek to Latin.csv',
    'nuts_codes_country': 'nuts_codes_country.yml',
}

NUTSPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['nutsAllLevels'])
NUTSCODESPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['nuts_codes_country'])

with open(NUTSCODESPATH, "r") as fh:
    CODESCOUNTRY = yaml.load(fh, Loader=yaml.SafeLoader)
COUNTRYCODES = {v: k for k,v in CODESCOUNTRY.items()}


