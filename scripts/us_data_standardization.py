# =============================================================================
# Script to standardize US data to Geodemograph inputs:
#
#     0. Age and gender distributions per geoUnit (state and counties)
#     0.  distributions
# =============================================================================

import os
import csv
import copy
import tempfile
# import yaml
# import json

from somecens.epo.tools import getMetadata

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
FOLDER = os.path.join(DIRPATH, "data/us")
DEFAULTYEAR = 5
DATAPATH = os.path.join(FOLDER, "cc-est2023-alldata.csv")
GEOUNITSPATH = os.path.join(FOLDER, f"us_geoUnits_year2023.csv")
MDYEAR = 2025
EPODBPATH = os.path.join(FOLDER, f"us_{MDYEAR}_pseudonymized_alldata.db")
METADATAPATH = os.path.join(FOLDER, f"us_metadata{MDYEAR}.csv")

# YEARDICT = {
#     1: "4/1/2020",
#     2: "7/1/2020",
#     3: "7/1/2021",
#     4: "7/1/2022",
#     5: "7/1/2023",
# }

# AGEDICT : {
#     0: "Total",
#     1: "Age 0 to 4 years",
#     2: "Age 5 to 9 years",
#     3: "Age 10 to 14 years",
#     4: "Age 15 to 19 years",
#     5: "Age 20 to 24 years",
#     6: "Age 25 to 29 years",
#     7: "Age 30 to 34 years",
#     8: "Age 35 to 39 years",
#     9: "Age 40 to 44 years",
#     10: "Age 45 to 49 years",
#     11: "Age 50 to 54 years",
#     12: "Age 55 to 59 years",
#     13: "Age 60 to 64 years",
#     14: "Age 65 to 69 years",
#     15: "Age 70 to 74 years",
#     16: "Age 75 to 79 years",
#     17: "Age 80 to 84 years",
#     18: "Age 85 years or older",
# }


parent_cmd = f"""
    xan filter \"col('YEAR') eq 5\" {DATAPATH} | \
    xan filter \"col('AGEGRP') eq 0 \" | \
"""

# 1. Parse data to get geoUnits (states and counties)

# 1.1 Counties
county_units = os.path.join(FOLDER, "us_counties_geounits_year2023.csv")
cmd = parent_cmd + f"""
    xan select STATE,COUNTY,CTYNAME | \
    xan rename parent_code,code,label | \
    xan map '\"US\" as country_code' | \
    xan map '\"2\" as level' | \
    xan map --overwrite 'parent_code ++ code as code' | \
    xan dedup | \
    xan select code,label,country_code,level,parent_code \
    > {county_units}
"""
os.system(cmd)

# 1.2 States
state_units = os.path.join(FOLDER, "us_states_geounits_year2023.csv")

cmd = parent_cmd + f"""
    xan select STATE,STNAME | \
    xan rename code,label | \
    xan map '\"US\" as country_code' | \
    xan map '\"1\" as level' | \
    xan map '"0" as parent_code' | \
    xan dedup | \
    xan select code,label,country_code,level,parent_code \
    > {state_units}
"""
os.system(cmd)

# 1.3 Country
country_units = os.path.join(FOLDER, "us_country_geounits_year2023.csv")
with open(country_units, "w") as f:
    f.writelines([
        "code,label,country_code,level,parent_code\n",
        "0,Usa,US,0,\n"
    ])

# 1.4 Concatenate all
units = os.path.join(FOLDER, "us_geounits_year2023.csv")
with tempfile.NamedTemporaryFile() as t1:
    os.system(f"xan cat rows {country_units} {state_units} > {t1.name}")
    os.system(f"xan cat rows {t1.name} {county_units} | xan sort -s code > {units}")
print(f"Csv file with us geographical units saved at {units}")
os.system(f"xan head {units} | xan v")


# 2. Parse data to get gender and age distributions

# 2.1 Gender distributions

# 2.1.1 Counties
county_genderDist = os.path.join(FOLDER, "us_counties_genreDists_year2023.csv")
cmd = parent_cmd + f"""
    xan select STATE,COUNTY,TOT_POP,TOT_MALE,TOT_FEMALE | \
    xan map --overwrite 'STATE ++ COUNTY as code' | \
    xan rename total,male,female,code -s TOT_POP,TOT_MALE,TOT_FEMALE,code | \
    xan select total,male,female,code | \
    xan map '\"2023\" as year' \
    > {county_genderDist}
"""

os.system(cmd)
print(f"Csv file with us counties gender distributions units saved at {county_genderDist}")
os.system(f"xan head {county_genderDist} | xan v")

# 2.1.2 States
state_genderDist = os.path.join(FOLDER, "us_states_genreDists_year2023.csv")
with tempfile.NamedTemporaryFile() as t:
        with tempfile.NamedTemporaryFile() as tT:
            with tempfile.NamedTemporaryFile() as tM:
                with tempfile.NamedTemporaryFile() as tF:
                    for file, CAT in zip([tT.name, tM.name, tF.name], ['TOT_POP', 'TOT_MALE', 'TOT_FEMALE']):
                        cmd = parent_cmd + f"""
                            xan select STATE,TOT_POP,TOT_MALE,TOT_FEMALE | \
                            xan groupby STATE 'sum({CAT})' \
                            > {file}
                        """
                        os.system(cmd)
                    os.system(f"xan join STATE {tT.name} STATE {tM.name} > {t.name}")
                    os.system(f"xan join STATE {t.name} STATE {tF.name} > {state_genderDist}")
                    cmd = f"xan select STATE,'sum(TOT_POP)','sum(TOT_MALE)','sum(TOT_FEMALE)' {state_genderDist} "
                    cmd += " | xan rename code,total,male,female "
                    cmd += " | xan map '\"2023\" as year'"
                    cmd += " | xan select total,male,female,code,year"
                    cmd += f" > {t.name}"
                    os.system(cmd)
                    os.system(f"mv {t.name} {state_genderDist}")
print(f"Csv file with us state gender distributions units saved at {state_genderDist}")
os.system(f"xan head {state_genderDist} | xan v")

# 2.1.3 Country
country_genderDist = os.path.join(FOLDER, "us_country_genreDists_year2023.csv")
cmd = f"xan agg --along-cols total,male,female 'sum(_)' {state_genderDist}"
cmd += " | xan map '\"2023\" as year'"
cmd += " | xan map '\"0\" as code'"
cmd += " | xan select total,male,female,code,year"
cmd += f" > {country_genderDist}"
os.system(cmd)
print(f"Csv file with us country gender distributions units saved at {country_genderDist}")
os.system(f"xan head {country_genderDist} | xan v")

# 2.1.3 All
genderDist = os.path.join(FOLDER, "us_genre_distribution_year2023.csv")
cmd = f"xan cat rows {country_genderDist} {state_genderDist} {county_genderDist} > {genderDist}"
os.system(cmd)
print(f"US gender distribution csv file saved at {genderDist}")
os.system(f"xan head {genderDist} | xan v")


# 2.2 Age distributions [TO DO]

# 3. Load metadata using auxiliar methods to request epo databases,
# then export as csv

# columns = ['pseudo_id', 'location', 'screen_name']
# metadata = getMetadata(EPODBPATH, columns=columns, not_null_column="location")

# metadatapath = os.path.join(FOLDER, f"us_metadata{MDYEAR}.csv")
# with open(metadatapath, 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(columns)
#     writer.writerows(metadata)
# print(f"Csv metadata file saved at {METADATAPATH}")

