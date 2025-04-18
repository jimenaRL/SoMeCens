import csv
import yaml
import sqlite3
import tempfile
import subprocess
from glob import glob
import concurrent.futures
from string import Template
from subprocess import Popen, PIPE

with open('nuts_codes_country.yml', "r") as fh:
    codes_country = yaml.load(fh, Loader=yaml.SafeLoader)
country_codes = {v: k for k,v in codes_country.items()}

with open('epo_country_years_in_nuts.yml', "r") as fh:
    country_years = yaml.load(fh, Loader=yaml.SafeLoader)

# print(codes)
# print(country_years)

db = "pseudonymized_alldata"
# pathPattern = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"
pathPattern = "${country}_${year}_${db}.db"

fields = ['screen_name', 'name', 'description', 'location']
table = "metadata"
QUERY = f"SELECT {','.join(fields)} FROM {table}"

NUTSLEVELS = [1, 2, 3]

def getLocationsLevel(country, level):
    code = country_codes[country]
    f1 = f"col('Country Code') eq '{code}'"
    f2 = f"col('NUTS level') eq {level}"
    s = f"NUTS level {level}"
    p1 = Popen(["xan", "filter", f1, "nuts.csv"], stdout=PIPE)
    p2 = Popen(["xan", "filter", f2], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["xan", "select", s], stdin=p2.stdout, stdout=PIPE)
    output = p3.communicate()[0].decode().split('\n')[1:-1]
    return output

def getLocations(country):
    return {level: getLocationsLevel(country, level) for level in NUTSLEVELS}

def getLastRelease(db, country, year):
    path = Template(pathPattern).substitute(db=db, country=country, year=year)
    canditates_paths = glob(path)
    canditates_paths.sort()
    last_release_path = canditates_paths[-1]
    print(f"Found last release at {last_release_path}.")
    return last_release_path

def getMetadata(dbpath):
    with sqlite3.connect(dbpath) as con:
        cur = con.cursor()
        cur.execute(QUERY)
        res = cur.fetchall()
    return res

def countOccurrences(file, term, level):
    p = Popen(['xan', 'search', term, file], stdout=PIPE)
    q = Popen(["xan", "count"], stdin=p.stdout, stdout=PIPE)
    output = q.communicate()[0].decode()
    nb_occurrence = int(output)
    # print(f"Found {nb_occurrence} times the term {term} in level {level}")
    return level, term, nb_occurrence

def writeMetadata(file, metadata):
    with open(file, 'w') as f:
        w = csv.writer(f)
        w.writerow(fields)
        w.writerows(metadata)

def pipeline(country, year):
    counts = {level: {} for level in NUTSLEVELS}
    locations = getLocations(country)
    dbpath = getLastRelease(db, country, year)
    metadata = getMetadata(dbpath)
    with tempfile.NamedTemporaryFile() as tmp:
        # write metada to tmp file
        writeMetadata(file=tmp.name, metadata=metadata)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # launch multiple threads
            futures = [
                executor.submit(countOccurrences, tmp.name, loc, level)
                for level in locations
                    for loc in locations[level]]
            # and collect results
            results = [f.result() for f in futures]
    for result in results:
        counts[result[0]][result[1]] = result[2]
    return counts

if __name__ == "__main__":

    print(yaml.dump(pipeline('belgium', '2020')))

    # for year in country_years:
    #     for country in country_years[year]:
    #         counts = pipeline(country, year)
    #         print(yaml.dump(counts))
    #         break
    #     break
