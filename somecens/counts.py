import os
import yaml
import tempfile
import concurrent.futures
from subprocess import Popen, PIPE
from argparse import ArgumentParser

from conf import DEFAULTDB, DEFAULTDBPATTERN, METADATAFIELDS, NUTSLEVELS
from tools import getLastRelease, getLocations, getMetadata, writeCsv

def countOccurrences(file, term, level):
    p = Popen(['xan', 'search', term, file], stdout=PIPE)
    q = Popen(["xan", "count"], stdin=p.stdout, stdout=PIPE)
    output = q.communicate()[0].decode()
    nb_occurrence = int(output)
    return level, term, nb_occurrence

def countTotal(file):
    qt = Popen(["xan", "count", file], stdout=PIPE)
    output = qt.communicate()[0].decode()
    nb_occurrence = int(output)
    return nb_occurrence

def pipeline(dbpath):
    counts = {level: {} for level in NUTSLEVELS}
    locations = getLocations(country)
    metadata = getMetadata(dbpath)
    with tempfile.NamedTemporaryFile() as tmp:
        # write metadata to tmp file
        writeCsv(tmp.name, metadata, headers=METADATAFIELDS)
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
    ap.add_argument('--dbpattern', type=str, default=DEFAULTDBPATTERN, required=False)
    ap.add_argument('--output', type=str, default='nutsCounts', required=False)

    args = ap.parse_args()
    country = args.country
    year = args.year
    db = args.db
    dbpattern = args.dbpattern
    output = args.output

    if not (country and year):
        country_years = COUNTRYEARS
    else:
        country_years = {year: [country]}

    for year in country_years:
        for country in country_years[year]:
            dbpath = getLastRelease(dbpattern, db, country, year)
            counts = pipeline(dbpath)
            filename = f'{output}/{country}_{year}'
            with open(f'{filename}.yml', 'w') as file:
                yaml.dump(counts, file)
            writeCsv(
                f'{filename}.csv',
                flatten(counts),
                headers=['field', 'value','count'])
            os.system(f"cat {filename}.yml")
            os.system(f"xan hist {filename}.csv")
