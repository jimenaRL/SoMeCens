import os
import yaml

DIRPATH = os.path.dirname(os.path.realpath(__file__))
DATAFOLDERPATH =  os.path.join(DIRPATH, 'data')

NUTSLEVELS = [1, 2, 3]

NUTSFILES = {
    'nuts1': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2024.csv',
    'statistical_regions': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Statistical Regions.csv',
    'allLevels': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2021- NUTS2024.csv',
    'nutsCyrillicGreekLatin': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Cyrillic & Greek to Latin.csv',
    'nuts3_total': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 1_Total.csv',
    'nuts3_males': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 2_Males.csv',
    'nuts3_females': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 3_Females.csv',
    'codes_country': 'nuts_codes_country.yml',
    'flattenStructure': 'nuts_flatten.csv',
    'flattenAgeDistributions': 'nuts_age_latten.csv',
}

NUTSPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['allLevels'])
NUTSCODESPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['codes_country'])
NUTSFLATTENPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['flattenStructure'])
NUTS3TOTAL = os.path.join(DATAFOLDERPATH, NUTSFILES['nuts3_total'])
NUTS3MALES = os.path.join(DATAFOLDERPATH, NUTSFILES['nuts3_males'])
NUTS3FEMALES = os.path.join(DATAFOLDERPATH, NUTSFILES['nuts3_females'])
NUTS3AGEFLATTENPATH = os.path.join(DATAFOLDERPATH, NUTSFILES['flattenAgeDistributions'])

with open(NUTSCODESPATH, "r") as fh:
    CODESCOUNTRY = yaml.load(fh, Loader=yaml.SafeLoader)
COUNTRYCODES = {v: k for k,v in CODESCOUNTRY.items()}
