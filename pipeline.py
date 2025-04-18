import csv
import yaml
import sqlite3
import tempfile
import pandas as pd
import subprocess
from subprocess import Popen, PIPE
from glob import glob
from string import Template

with open('nuts_codes_country.yml', "r") as fh:
    codes_country = yaml.load(fh, Loader=yaml.SafeLoader)
country_codes = {v: k for k,v in codes_country.items()}

with open('epo_country_years_in_nuts.yml', "r") as fh:
    country_years = yaml.load(fh, Loader=yaml.SafeLoader)

# print(codes)
# print(country_years)

db = "pseudonymized_alldata"
pathPattern = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"

fields = ['screen_name', 'name', 'description', 'location']
table = "metadata"
query = f"SELECT {','.join(fields)} FROM {table}"

dfnuts = pd.read_csv("nuts.csv")

def getNutsXan(country, level):
    code = 'BE';
    lecel = 1;
    country_codes[country]
    f1 = Template("col('Country Code') eq '${code}'").substitute(code=code)
    f2 = Template("col('NUTS level') eq ${level}").substitute(level=level)
    s = f"NUTS level {level}"
    p1 = Popen(["xan", "filter", f1, "nuts.csv"], stdout=PIPE)
    p2 = Popen(["xan", "filter", f2], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["xan", "select", s], stdin=p2.stdout, stdout=PIPE)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    p2.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p3.communicate()[0]
    print(output)

def getNuts(country, level):
    code = country_codes[country]
    names = dfnuts[dfnuts['Country Code'] == code]
    names = names[names['NUTS level'] == level]
    names = names[f"NUTS level {level}"].tolist()
    return names

def pipeline(country, year, nuts):
    canditates = glob(Template(pathPattern).substitute(
        db=db, country=country, year=year))
    canditates.sort()
    last_release_path = canditates[-1]
    with sqlite3.connect(last_release_path) as con:
        cur = con.cursor()
        cur.execute(query)
        res = cur.fetchall()
    with tempfile.NamedTemporaryFile() as tmp:
       with open(tmp.name, 'w') as f:
           w = csv.writer(f)
           w.writerow(fields)
           w.writerows(res)
       command_xan = ['xan', 'v', tmp.name]
       subprocess.run(command_xan)
       print(nuts)

for year in country_years:
    for country in country_years[year]:
        nuts = {level: getNuts(country, level) for level in [1, 2, 3]}
        pipeline(country, year, nuts)
        break
    break
