import os
import yaml

DIR = os.path.dirname(os.path.realpath(__file__))
DATAFOLDER =  os.path.join(DIR, 'data')

LEVELS = [1, 2, 3]

FILES = {
    # 'nuts1': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2024.csv',
    # 'statistical_regions': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Statistical Regions.csv',
    'allLevels': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - NUTS2021- NUTS2024.csv',
    # 'nutsCyrillicGreekLatin': 'NUTS2021-NUTS2024_codes_NUTS123_to_NUTS1.xlsx - Cyrillic & Greek to Latin.csv',
    'nuts3_total': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 1_Total.csv',
    'nuts3_males': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 2_Males.csv',
    'nuts3_females': 'NUTS123_Y2015_2024_Gender.xlsx - Sheet 3_Females.csv',
    'codes_country': 'nuts_codes_country.yml',
    'flattenStructure2021': 'nuts_flatten_2021.csv',
    'flattenStructure2024': 'nuts_flatten_2024.csv',
    'flattenGenderDistributions2024': 'nuts_gender_flatten_2024.csv',
    'flattenGenderDistributions2021': 'nuts_gender_flatten_2021.csv',
}

ALLLEVELS = os.path.join(DATAFOLDER, FILES['allLevels'])
CODES = os.path.join(DATAFOLDER, FILES['codes_country'])
FLATTEN2021 = os.path.join(DATAFOLDER, FILES['flattenStructure2021'])
FLATTEN2024 = os.path.join(DATAFOLDER, FILES['flattenStructure2024'])

NUTS3GENDERMALES = os.path.join(DATAFOLDER, FILES['nuts3_males'])
NUTS3GENDERFEMALES = os.path.join(DATAFOLDER, FILES['nuts3_females'])
NUTS3GENDERTOTAL = os.path.join(DATAFOLDER, FILES['nuts3_total'])
NUTS3GENDERFLATTEN2024 = os.path.join(DATAFOLDER, FILES['flattenGenderDistributions2024'])
NUTS3GENDERFLATTEN2021 = os.path.join(DATAFOLDER, FILES['flattenGenderDistributions2021'])

with open(CODES, "r") as fh:
    CODESCOUNTRY = yaml.load(fh, Loader=yaml.SafeLoader)
COUNTRYCODES = {v: k for k,v in CODESCOUNTRY.items()}
