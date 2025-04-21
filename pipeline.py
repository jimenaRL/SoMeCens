import os
import csv
import yaml
import sqlite3
import tempfile
import subprocess
from glob import glob
import concurrent.futures
from string import Template
from subprocess import Popen, PIPE
from argparse import ArgumentParser


COUNTRYEARSFILE = 'epo_country_years_in_nuts.yml'

with open('nuts_codes_country.yml', "r") as fh:
    codes_country = yaml.load(fh, Loader=yaml.SafeLoader)
country_codes = {v: k for k,v in codes_country.items()}

DEFAULTDB = "pseudonymized_alldata"
DEFAULTPATTERN = "/mnt/hdd2/epodata/stage/*/${db}/${country}_${year}_${db}.db"

FIELDS = ['screen_name', 'name', 'description', 'location']
TABLE = "metadata"
QUERY = f"SELECT {','.join(FIELDS)} FROM {TABLE}"

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

def getLastRelease(pathPattern, db, country, year):
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

def writeMetadata(file, metadata):
    with open(file, 'w') as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        w.writerows(metadata)

def countOccurrences(file, term, level):
    p = Popen(['xan', 'search', term, file], stdout=PIPE)
    q = Popen(["xan", "count"], stdin=p.stdout, stdout=PIPE)
    output = q.communicate()[0].decode()
    nb_occurrence = int(output)
    return level, term, nb_occurrence

def countTotal(file):
    q = Popen(["xan", "count", file], stdout=PIPE)
    output = q.communicate()[0].decode()
    nb_occurrence = int(output)
    return nb_occurrence

def pipeline(dbpath):
    counts = {level: {} for level in NUTSLEVELS}
    locations = getLocations(country)
    metadata = getMetadata(dbpath)
    with tempfile.NamedTemporaryFile() as tmp:
        # write metadata to tmp file
        writeMetadata(file=tmp.name, metadata=metadata)
        # get total count
        total_count = countTotal(file=tmp.name)
        # launch multiple threads searching locations terms with xan
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(countOccurrences, tmp.name, loc, level)
                for level in locations
                    for loc in locations[level]]
            # and collect results
            results = [f.result() for f in futures]

    for result in results:
        counts[result[0]][result[1]] = result[2]

    # add total number of no matches
    for level in NUTSLEVELS:
        total_level = sum([r[2] for r in results if r[0] == level])
        counts[level]["NO FOUND LOCATION"] = total_count - total_level

    return counts

def flatten(counts):
    return [
        (level, term, count)
        for level in NUTSLEVELS
        for term, count in counts[level].items()
    ]

if __name__ == "__main__":

    ap = ArgumentParser()
    ap.add_argument('--country', type=str, default=None, required=False)
    ap.add_argument('--year', type=str, default=None, required=False)
    ap.add_argument('--db', type=str, default=DEFAULTDB, required=False)
    ap.add_argument('--pattern', type=str, default=DEFAULTPATTERN, required=False)
    ap.add_argument('--output', type=str, default='nutsCounts', required=False)

    args = ap.parse_args()
    country = args.country
    year = args.year
    db = args.db
    pattern = args.pattern
    output = args.output

    if not country and year:
        with open(COUNTRYEARSFILE, "r") as fh:
            country_years = yaml.load(fh, Loader=yaml.SafeLoader)
    else:
        country_years = {year: [country]}

    for year in country_years:
        for country in country_years[year]:
            dbpath = getLastRelease(pattern, db, country, year)
            counts = pipeline(dbpath)
            filename = f'{output}/{country}_{year}'
            with open(f'{filename}.yml', 'w') as file:
                yaml.dump(counts, file)
            with open(f'{filename}.csv', 'w') as file:
                writer =  csv.writer(file)
                writer.writerow(['field', 'value','count'])
                writer.writerows(flatten(counts))
            os.system(f"cat {filename}.yml")
            os.system(f"xan hist {filename}.csv")
