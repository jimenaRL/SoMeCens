# =============================================================================
# Script to standardize Chle data to Geodemograph inputs
#
# Original data obtained from https://censo2024.ine.gob.cl/estadisticas/
# "Fuente: Censo de Población y Vivienda 2024 - Instituto Nacional de Estadísticas.
# =============================================================================

import os
import csv
import tempfile
from string import Template

from somecens.epo.tools import getMetadata

DIRPATH = os.environ['SOMECENSDIR'] if 'SOMECENSDIR' in os.environ else '.'
FOLDER = os.path.join(DIRPATH, "data/chile")
COMUNASDATAPATH = os.path.join(FOLDER, "D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx-4.csv")
REGIONDATAPATH = os.path.join(FOLDER, "D1_Poblacion-censada-por-sexo-y-edad-en-grupos-quinquenales.xlsx-3.csv")
CENSUSYEAR = 2024
GEOUNITSPATH = os.path.join(FOLDER, f"chile_geoUnits_census_{CENSUSYEAR}.csv")
EPODATAYEARS = [2020, 2023, 2025]

EPODBPATH = "/mnt/hdd2/epodata/stage/20250929/pseudonymized_alldata/chile_${epodatayear}_pseudonymized_alldata.db"
IDSDBPATH = "/mnt/hdd2/epodata/stage/20250929/lut/chile_${epodatayear}_lut.db"
METADATAPATH = os.path.join(FOLDER, "chile_metadata_epo_${epodatayear}.csv")

# 1. Parse data to get geoUnits (states and counties)

# Level 3: comunas
comunas_units = os.path.join(FOLDER, f"chile_comunas_geounits_census_{CENSUSYEAR}.csv")
cmd = f"""
    xan select Comuna,'Código comuna','Código provincia' {COMUNASDATAPATH} | \
    xan rename label,code,parent_code | \
    xan dedup | \
    xan map '3 as level' | \
    xan map 'concat(\"p\", parent_code) as pparent_code' | \
    xan select label,code,level,pparent_code | \
    xan rename label,code,level,parent_code | \
    xan search --invert-match País > {comunas_units}
"""
os.system(cmd)
os.system(f"xan v {comunas_units}")


# Level 2: provincias
provincias_units = os.path.join(FOLDER, f"chile_provincias_geounits_census_{CENSUSYEAR}.csv")
cmd = f"""
    xan select Provincia,'Código provincia','Código región' {COMUNASDATAPATH} | \
    xan rename label,code,parent_code | \
    xan dedup | \
    xan map 'concat(\"p\", code) as pcode' | \
    xan map '2 as level' | \
    xan map '2 as level' | \
    xan select label,pcode,level,parent_code | \
    xan rename label,code,level,parent_code | \
    xan search --invert-match País > {provincias_units}
"""
os.system(cmd)
os.system(f"xan v {provincias_units}")


# Level 1: regions
regions_units = os.path.join(FOLDER, f"chile_regions_geounits_census_{CENSUSYEAR}.csv")
cmd = f"""
    xan select Región,'Código región' {COMUNASDATAPATH} | \
    xan rename label,code | \
    xan dedup | \
    xan map '0 as parent_code' | \
    xan map '1 as level' | \
    xan select label,code,level,parent_code | \
    xan search --invert-match País > {regions_units}
"""
os.system(cmd)
os.system(f"xan v {regions_units}")

# Level 0: pais
country_units = os.path.join(FOLDER, f"chile_pais_geounits_census_{CENSUSYEAR}.csv")
with open(country_units, "w") as f:
    f.writelines([
        "label,code,level,parent_code\n",
        "Chile,0,0,\n"
    ])

# 1.4 Concatenate all
units = os.path.join(FOLDER, f"chile_geounits_census_{CENSUSYEAR}.csv")
with tempfile.NamedTemporaryFile() as t:
    with open(t.name, "w") as f:
        f.writelines('\n'.join([country_units, regions_units, provincias_units, comunas_units]))
    os.system(f"xan cat rows --paths {t.name} > {units}")
print(f"Csv file with us geographical units saved at {units}")
os.system(f"xan v {units}")

# 2. Parse data to get gender and age distributions

age_3_path = os.path.join(FOLDER, f"chile_comunas_ageDists_census_{CENSUSYEAR}.csv")
cmd =  f"""
    xan search --invert-match País {COMUNASDATAPATH} | \
    xan select Comuna,'Código comuna','Código provincia','Grupos de edad','Población censada' | \
    xan rename label,code,parent_code,age,total | \
    xan map "replace(total, ' ', '') as total_as_number" | \
    xan map 'concat(\"p\", parent_code) as pparent_code' | \
    xan select  label,code,pparent_code,age,total_as_number | \
    xan rename  label,code,parent_code,age,total | \
    xan search "Total Comuna" --replace "Total" > {age_3_path}
"""
os.system(cmd)
os.system(f"xan v {age_3_path}")


age_2_path = os.path.join(FOLDER, f"chile_provincias_ageDists_census_{CENSUSYEAR}.csv")
cmd1 = f"""
    xan groupby parent_code,age 'sum(total)' {age_3_path} | \
    xan rename code,age,total > /tmp/tmp.csv
"""
cmd2 = f"""
    xan join --left code /tmp/tmp.csv code {provincias_units} | \
    xan select label,code,parent_code,age,total > {age_2_path}
"""
os.system(cmd1)
os.system(cmd2)
os.system(f"xan v {age_2_path}")


age_1_path = os.path.join(FOLDER, f"chile_regiones_ageDists_census_{CENSUSYEAR}.csv")
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

age_0_path = os.path.join(FOLDER, f"chile_pais_ageDists_census_{CENSUSYEAR}.csv")
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

ageDist = os.path.join(FOLDER, f"chile_age_distribution_census_{CENSUSYEAR}.csv")
cmd = f"xan cat rows {age_0_path} {age_1_path} {age_2_path} {age_3_path} > {ageDist}"
os.system(cmd)
os.system(f"xan v {ageDist}")

os.system(f"rm {age_0_path} {age_1_path} {age_2_path} {age_3_path}")


# 2.1 Gender distributions

gender_3_path = os.path.join(FOLDER, f"chile_comunas_genderDists_census_{CENSUSYEAR}.csv")
cmd =  f"""
    xan search --invert-match País {COMUNASDATAPATH} | \
    xan filter "col('Grupos de edad') eq 'Total Comuna'" | \
    xan select Comuna,'Código comuna','Código provincia','Población censada',Hombres,Mujeres | \
    xan rename label,code,parent_code,total,male,female | \
    xan map "replace(total, ' ', '') as total_as_number" | \
    xan map "replace(male, ' ', '') as male_as_number" | \
    xan map "replace(female, ' ', '') as female_as_number" | \
    xan map 'concat(\"p\", parent_code) as pparent_code' | \
    xan select  label,code,pparent_code,total_as_number,male_as_number,female_as_number | \
    xan rename  label,code,parent_code,total,male,female | \
    xan search "Total Comuna" --replace "Total" > {gender_3_path}
"""
os.system(cmd)
os.system(f"xan v {gender_3_path}")

gender_2_path = os.path.join(FOLDER, f"chile_provincias_genderDists_census_{CENSUSYEAR}.csv")
cmdt = f"""
    xan groupby parent_code 'sum(total)' {gender_3_path} | \
    xan rename code,total > /tmp/tmp_total.csv
"""
cmdm = f"""
    xan groupby parent_code 'sum(male)' {gender_3_path} | \
    xan rename code,male > /tmp/tmp_male.csv
"""
cmdf = f"""
    xan groupby parent_code 'sum(female)' {gender_3_path} | \
    xan rename code,female > /tmp/tmp_female.csv
"""
cmd1 = "xan join code /tmp/tmp_male.csv code /tmp/tmp_total.csv > /tmp/tmp_totalmale.csv "
cmd2 = "xan join code /tmp/tmp_totalmale.csv code /tmp/tmp_female.csv > /tmp/tmp.csv "

cmd = f"""
    xan join code /tmp/tmp.csv code {provincias_units} | \
    xan select label,code,parent_code,total,male,female > {gender_2_path}
"""

os.system(cmdt)
os.system(cmdm)
os.system(cmdf)
os.system(cmd1)
os.system(cmd2)
os.system(cmd)

os.system(f"xan v {gender_2_path}")


gender_1_path = os.path.join(FOLDER, f"chile_regiones_genderDists_census_{CENSUSYEAR}.csv")
cmd =  f"""
    xan search --invert-match País {REGIONDATAPATH} | \
    xan filter "col('Grupos de edad') eq 'Total Región'" | \
    xan select Región,'Código región','Población censada',Hombres,Mujeres | \
    xan rename label,code,total,male,female | \
    xan map '0 as parent_code' | \
    xan map "replace(total, ' ', '') as total_as_number" | \
    xan map "replace(male, ' ', '') as male_as_number" | \
    xan map "replace(female, ' ', '') as female_as_number" | \
    xan select  label,code,parent_code,total_as_number,male_as_number,female_as_number | \
    xan rename  label,code,parent_code,total,male,female > {gender_1_path}
"""
os.system(cmd)
os.system(f"xan v {gender_1_path}")

gender_0_path = os.path.join(FOLDER, f"chile_pais_genderDists_census_{CENSUSYEAR}.csv")
cmdt = f"xan agg --along-cols total 'sum(_)' {gender_1_path} > /tmp/chiletotal.csv"
cmdm = f"xan agg --along-cols male 'sum(_)' {gender_1_path} > /tmp/chilemale.csv"
cmdf = f"xan agg --along-cols female 'sum(_)' {gender_1_path} > /tmp/chilefemale.csv"
cmd = f"""
    xan cat columns /tmp/chilefemale.csv /tmp/chilemale.csv /tmp/chiletotal.csv | \
    xan map '\"\" as parent_code' | \
    xan map '0 as code' | \
    xan map '0 as level' | \
    xan map '\"Chile\" as label' | \
    xan select label,code,parent_code,total,male,female  > {gender_0_path}
"""
os.system(cmdt)
os.system(cmdm)
os.system(cmdf)
os.system(cmd)
os.system(f"xan v {gender_0_path}")


genderDist = os.path.join(FOLDER, f"chile_gender_distribution_census_{CENSUSYEAR}.csv")
cmd = f"xan cat rows {gender_0_path} {gender_1_path} {gender_2_path} {gender_3_path} > {genderDist}"
os.system(cmd)
os.system(f"xan v {genderDist}")

os.system(f"rm {gender_0_path} {gender_1_path} {gender_2_path} {gender_3_path}")

os.system(f"rm {country_units} {regions_units} {provincias_units} {comunas_units}")

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
