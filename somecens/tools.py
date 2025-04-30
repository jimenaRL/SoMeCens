import csv
import sqlite3
from glob import glob
from string import Template
from subprocess import Popen, PIPE

from conf import \
    COUNTRYCODES, \
    NUTSLEVELS, \
    METADATAFIELDS, \
    METADATATABLE, \
    NUTSPATH

QUERY = f"SELECT {','.join(METADATAFIELDS)} FROM {METADATATABLE}"

def writeCsv(file, rows, headers=None, verbose=False):
    with open(file, 'w') as f:
        writer =  csv.writer(f)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)
    if verbose:
        print(f"Csv file saved at {file}.")

def getNutsLocationsLevel(country, level):
    code = COUNTRYCODES[country]
    f1 = f"col('Country Code') eq '{code}'"
    f2 = f"col('NUTS level') eq {level}"
    s = f"NUTS level {level}"
    p1 = Popen(["xan", "filter", f1, NUTSPATH], stdout=PIPE)
    p2 = Popen(["xan", "filter", f2], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["xan", "select", s], stdin=p2.stdout, stdout=PIPE)
    output = p3.communicate()[0].decode().split('\n')[1:-1]
    return output

def getNutsLocations(country, format='dict'):
    locsDict = {level: getNutsLocationsLevel(country, level) for level in NUTSLEVELS}
    if format == 'dict':
        return locsDict
    elif format == 'flatten':
        return [(loc, level) for level in locsDict for loc in locsDict[level]]
    else:
        raise ValueError(f"Format must be 'dict' or 'flatten'. Found {format}")

def getLastRelease(pathPattern, db, country, year):
    path = Template(pathPattern).substitute(db=db, country=country, year=year)
    canditates_paths = glob(path)
    if len(canditates_paths) == 0:
        raise ValueError(f"No canditate paths found at {path}.")
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
