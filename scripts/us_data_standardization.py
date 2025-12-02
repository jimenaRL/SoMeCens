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
import json

from somecens.epo.tools import getMetadata

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
FOLDER = os.path.join(DIRPATH, "data/us")
DEFAULTYEAR = 5
DATAPATH = os.path.join(FOLDER, "cc-est2023-alldata.csv")
GEOUNITSPATH = os.path.join(FOLDER, f"us_geoUnits_year2023.csv")
EPODATAYEARS = [2020, 2023, 2025]
EPODBPATH = "/mnt/hdd2/epodata/stage/20250929/pseudonymized_alldata/chile_${epodatayear}_pseudonymized_alldata.db"
IDSDBPATH = "/mnt/hdd2/epodata/stage/20250929/lut/chile_${epodatayear}_lut.db"
METADATAPATH = os.path.join(FOLDER, "us_metadata_epo_${epodatayear}.csv")

# YEARDICT = {
#     1: "4/1/2020",
#     2: "7/1/2020",
#     3: "7/1/2021",
#     4: "7/1/2022",
#     5: "7/1/2023",
# }

AGEDICT = {
    0: "Total",
    1: "Age 0 to 4 years",
    2: "Age 5 to 9 years",
    3: "Age 10 to 14 years",
    4: "Age 15 to 19 years",
    5: "Age 20 to 24 years",
    6: "Age 25 to 29 years",
    7: "Age 30 to 34 years",
    8: "Age 35 to 39 years",
    9: "Age 40 to 44 years",
    10: "Age 45 to 49 years",
    11: "Age 50 to 54 years",
    12: "Age 55 to 59 years",
    13: "Age 60 to 64 years",
    14: "Age 65 to 69 years",
    15: "Age 70 to 74 years",
    16: "Age 75 to 79 years",
    17: "Age 80 to 84 years",
    18: "Age 85 years or older",
}


parent_cmd = f"""
    xan filter \"col('YEAR') eq 5\" {DATAPATH} | \
    xan filter \"col('AGEGRP') eq 0 \" | \
"""

# 1. Parse data to get geoUnits (states and counties)

# 1.1 Counties
county_units = os.path.join(FOLDER, f"us_counties_geounits_cc-est_2023.csv")
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
state_units = os.path.join(FOLDER, f"us_states_geounits_cc-est_2023.csv")

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
country_units = os.path.join(FOLDER, f"us_country_geounits_cc-est_2023.csv")
with open(country_units, "w") as f:
    f.writelines([
        "code,label,country_code,level,parent_code\n",
        "0,Usa,US,0,\n"
    ])

# 1.4 Concatenate all
units = os.path.join(FOLDER, f"us_geounits_cc-est_2023.csv")
with tempfile.NamedTemporaryFile() as t1:
    os.system(f"xan cat rows {country_units} {state_units} > {t1.name}")
    os.system(f"xan cat rows {t1.name} {county_units} | xan sort -s code > {units}")
print(f"Csv file with us geographical units saved at {units}")
os.system(f"xan head {units} | xan v")


# 2. Parse data to get gender and age distributions

# 2.0 Age distributions

# 2.0.1 Counties
county_ageDist = os.path.join(FOLDER, f"us_counties_ageDists_cc-est_2023.csv")
age_parent_cmd  = f"""
    xan filter \"col('YEAR') eq 5\" {DATAPATH} | \
"""
cmd = age_parent_cmd + f"""
    xan select STATE,COUNTY,AGEGRP,TOT_POP | \
    xan map --overwrite 'STATE ++ COUNTY as code' | \
    xan rename total,age,code -s TOT_POP,AGEGRP,code | \
    xan select total,age,code | \
    xan map '\"{MDYEAR}\" as year' \
    > {county_ageDist}
"""
print(f"[RUNNING] {cmd}")
os.system(cmd)
print(f"Csv file with us counties age distributions units saved at {county_ageDist}")
os.system(f"xan head {county_ageDist} | xan v")

# 2.0.1 States
state_ageDist = os.path.join(FOLDER, f"us_states_ageDists_cc-est_2023.csv")
age_parent_cmd  = f"""
    xan filter \"col('YEAR') eq 5\" {DATAPATH} | \
"""
cmd = age_parent_cmd + f""" xan select STATE,COUNTY,AGEGRP,TOT_POP | \
    xan groupby STATE,AGEGRP 'sum(TOT_POP)' | \
    xan rename total,age,code | \
    xan select total,age,code | \
    xan map '\"{MDYEAR}\" as year' \
    > {state_ageDist}
"""
print(f"[RUNNING] {cmd}")
os.system(cmd)
print(f"Csv file with us state gender distributions units saved at {state_ageDist}")
os.system(f"xan head {state_ageDist} | xan v")

# 2.0.2 Country
country_ageDist = os.path.join(FOLDER, f"us_country_ageDists_cc-est_2023.csv")
cmd = f"xan groupby age,year 'sum(code)' {state_ageDist}"
cmd += " | xan map '\"0\" as code'"
cmd += " | xan rename age,year,total,code"
cmd += " | xan select total,age,code,year"
cmd += f" > {country_ageDist}"
print(f"[RUNNING] {cmd}")
os.system(cmd)
print(f"Csv file with us country gender distributions units saved at {country_ageDist}")
os.system(f"xan head {country_ageDist} | xan v")

# 2.0.3 All
ageDist = os.path.join(FOLDER, f"us_age_distribution_cc-est_2023.csv")
cmd = f"xan cat rows {country_ageDist} {state_ageDist} {county_ageDist} > {ageDist}"
print(f"[RUNNING] {cmd}")
os.system(cmd)
print(f"US gender distribution csv file saved at {ageDist}")
os.system(f"xan head {ageDist} | xan v")

# 2.1 Gender distributions

# 2.1.1 Counties
county_genderDist = os.path.join(FOLDER, "us_counties_genreDists_cc-est_2023.csv")
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
state_genderDist = os.path.join(FOLDER, "us_states_genreDists_cc-est_2023.csv")
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
country_genderDist = os.path.join(FOLDER, "us_country_genreDists_cc-est_2023.csv")
cmd = f"xan agg --along-cols total,male,female 'sum(_)' {state_genderDist}"
cmd += " | xan map '\"2023\" as year'"
cmd += " | xan map '\"0\" as code'"
cmd += " | xan select total,male,female,code,year"
cmd += f" > {country_genderDist}"
os.system(cmd)
print(f"Csv file with us country gender distributions units saved at {country_genderDist}")
os.system(f"xan head {country_genderDist} | xan v")

# 2.1.3 All
genderDist = os.path.join(FOLDER, "us_genre_distribution_cc-est_2023.csv")
cmd = f"xan cat rows {country_genderDist} {state_genderDist} {county_genderDist} > {genderDist}"
os.system(cmd)
print(f"US gender distribution csv file saved at {genderDist}")
os.system(f"xan head {genderDist} | xan v")


# 3. Load metadata using auxiliar methods to request epo databases,
# then export as csv

for year in EPODATAYEARS:
    metadata = getMetadata(
        dbpath=Template(EPODBPATH).safe_substitute(epodatayear=year),
        columns=['pseudo_id', 'location', 'screen_name'],
        not_null_column="location",
        ids_dbpath=Template(IDSDBPATH).safe_substitute(epodatayear=year))

    path = Template(METADATAPATH).safe_substitute(epodatayear=year)
    with open(path, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['twitter_id', 'location', 'screen_name'])
        writer.writerows(metadata)
    print(f"Csv metadata file saved at {path}")
    os.system(f"xan v {path}")
