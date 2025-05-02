import csv
from subprocess import Popen, PIPE

from somecens.nuts.conf  import \
    NUTSFLATTENPATH, \
    COUNTRYCODES, \
    NUTSLEVELS, \
    NUTSPATH

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

def getNuts(country):
    code = COUNTRYCODES[country]
    with open(NUTSFLATTENPATH, newline='') as csvfile:
        return [d for d in csv.DictReader(csvfile) if d['country_code'] == code]