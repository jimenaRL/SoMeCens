# =============================================================================
# Script to standardize Chle data to Geodemograph inputs
# =============================================================================

import os
import csv
import copy
import tempfile
# import yaml
import json

from somecens.epo.tools import getMetadata

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
FOLDER = os.path.join(DIRPATH, "data/chile")
COMUNASDATAPATH = os.path.join(FOLDER, "D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx-4.csv")
REGIONDATAPATH = os.path.join(FOLDER, "D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx-3.csv")
DATAYEAR = 2024
GEOUNITSPATH = os.path.join(FOLDER, f"chile_geoUnits.csv")
MDYEAR = 2023
EPODBPATH = os.path.join(FOLDER, f"chile_{MDYEAR}_pseudonymized_alldata.db")
# EPODBPATH = "/mnt/hdd2/epodata/production/v0/pseudonymized_alldata/us_2023_pseudonymized_alldata_20250416.db"
METACOMUNASDATAPATH = os.path.join(FOLDER, f"us_metadata{MDYEAR}.csv")

GRUPOSEDAD = [
    'Total País',
    '0 a 4',
    '5 a 9',
    '10 a 14',
    '15 a 19',
    '20 a 24',
    '25 a 29',
    '30 a 34',
    '35 a 39',
    '40 a 44',
    '45 a 49',
    '50 a 54',
    '55 a 59',
    '60 a 64',
    '65 a 69',
    '70 a 74',
    '75 a 79',
    '80 a 84',
    '85 o más',
    'Total Comuna',
    ''
]

# 1. Parse data to get geoUnits (states and counties)

# Level 3: comunas
comunas_units = os.path.join(FOLDER, f"chile_comunas_geounits_census_{DATAYEAR}.csv")
cmd = f"""
    xan select Comuna,'Código comuna','Código provincia' {COMUNASDATAPATH} | \
    xan rename label,code,parent_code | \
    xan dedup | \
    xan map '0 as country_code' | \
    xan map '3 as level' | \
    xan search --invert-match País > {comunas_units}
"""
os.system(cmd)
os.system(f"xan v {comunas_units}")

# Level 2: provincias
provincias_units = os.path.join(FOLDER, f"chile_provincias_geounits_census_{DATAYEAR}.csv")
cmd = f"""
    xan select Provincia,'Código provincia','Código región' {COMUNASDATAPATH} | \
    xan rename label,code,parent_code | \
    xan dedup | \
    xan map '0 as country_code' | \
    xan map '2 as level' | \
    xan search --invert-match País > {provincias_units}
"""
os.system(cmd)
os.system(f"xan v {provincias_units}")

# Level 1: regions
regions_units = os.path.join(FOLDER, f"chile_regions_geounits_census_{DATAYEAR}.csv")
cmd = f"""
    xan select Región,'Código región' {COMUNASDATAPATH} | \
    xan rename label,code | \
    xan dedup | \
    xan map '0 as parent_code' | \
    xan map '0 as country_code' | \
    xan map '1 as level' | \
    xan search --invert-match País > {regions_units}
"""
os.system(cmd)
os.system(f"xan v {regions_units}")

# Level 0: pais
country_units = os.path.join(FOLDER, f"chile_pais_geounits_census_{DATAYEAR}.csv")
with open(country_units, "w") as f:
    f.writelines([
        "label,code,country_code,level,parent_code\n",
        "Chile,0,0,0,\n"
    ])

# 1.4 Concatenate all
units = os.path.join(FOLDER, f"chile_geounits_census_{DATAYEAR}.csv")
with tempfile.NamedTemporaryFile() as t:
    with open(t.name, "w") as f:
        f.writelines('\n'.join([country_units, regions_units, provincias_units, comunas_units]))
    os.system(f"xan cat rows --paths {t.name} > {units}")
print(f"Csv file with us geographical units saved at {units}")
os.system(f"xan v {units}")

# 2. Parse data to get gender and age distributions

age_3_path = os.path.join(FOLDER, f"chile_comunas_ageDists_census_{DATAYEAR}.csv")
cmd =  f"""
    xan search --invert-match País {COMUNASDATAPATH} | \
    xan select Comuna,'Código comuna','Código provincia','Grupos de edad','Población censada' | \
    xan rename label,code,parent_code,age,total | \
    xan map "replace(total, ' ', '') as total_as_number" | \
    xan select  label,code,parent_code,age,total_as_number | \
    xan rename  label,code,parent_code,age,total | \
    xan search "Total Comuna" --replace "Total" > {age_3_path}
"""
os.system(cmd)
os.system(f"xan v {age_3_path}")

age_2_path = os.path.join(FOLDER, f"chile_provincias_ageDists_census_{DATAYEAR}.csv")
cmd1 = f"""
    xan groupby parent_code,age 'sum(total)' {age_3_path} | \
    xan rename code,age,total > /tmp/tmp.csv"
"""
cmd2 = f"""
    xan join --left code tmp.csv code {provincias_units} | \
    xan select label,code,parent_code,age,total > {age_2_path}
"""
os.system(cmd1)
os.system(cmd2)
os.system(f"rm /tmp/tmp.csv")
os.system(f"xan v {age_2_path}")

age_1_path = os.path.join(FOLDER, f"chile_regiones_ageDists_census_{DATAYEAR}.csv")
cmd =  f"""
    xan search --invert-match País {REGIONDATAPATH} | \
    xan select Región,'Código región','Grupos de edad','Población censada' | \
    xan rename label,code,age,total | \
    xan map '0 as parent_code' | \
    xan map "replace(total, ' ', '') as total_as_number" | \
    xan select  label,code,parent_code,age,total_as_number | \
    xan rename  label,code,parent_code,age,total | \
    xan search "Total Región" --replace "Total" > {age_1_path}
"""
os.system(cmd)
os.system(f"xan v {age_1_path}")

age_0_path = os.path.join(FOLDER, f"chile_pais_ageDists_census_{DATAYEAR}.csv")
cmd = f"""
    xan groupby age 'sum(total) as total' {age_1_path} | \
    xan map '\"\" as parent_code' | \
    xan map '0 as code' | \
    xan map '0 as level' | \
    xan map '\"Chile\" as label' | \
    xan select label,code,parent_code,age,total  > {age_0_path}
"""
os.system(cmd)
os.system(f"xan v {age_0_path}")

ageDist = os.path.join(FOLDER, f"chile_age_distribution_census_{DATAYEAR}.csv")
cmd = f"xan cat rows {age_0_path} {age_1_path} {age_2_path} {age_3_path} > {ageDist}"
os.system(cmd)
os.system(f"xan v {ageDist}")

exit()

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


# 3. Load metadata using auxiliar methods to request epo databases,
# then export as csv

columns = ['pseudo_id', 'location', 'screen_name']
metadata = getMetadata(EPODBPATH, columns=columns, not_null_column="location")

metadatapath = os.path.join(FOLDER, f"us_metadata{MDYEAR}.csv")
with open(metadatapath, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(columns)
    writer.writerows(metadata)
print(f"Csv metadata file saved at {METACOMUNASDATAPATH}")

