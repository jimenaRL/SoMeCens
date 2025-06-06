import os
import csv
from glob import glob
import pandas as pd
from subprocess import Popen, PIPE

from somecens.nuts.conf  import \
    NUTS3GENDERTOTAL, \
    NUTS3GENDERFEMALES, \
    NUTS3GENDERMALES, \
    FLATTEN2021, \
    FLATTEN2024, \
    COUNTRYCODES, \
    NUTS3AGEFOLDER, \
    NUTS3AGECATS, \
    LEVELS, \
    ALLLEVELS

def strToInt(string: str) -> int:
    return int(string.replace('\u202f', ''))

def getNutsLocationsLevel(country: str, level: int, year: int = 2024) -> str:
    code = COUNTRYCODES[country]
    f1 = f"col('Country Code') eq '{code}'"
    f2 = f"col('NUTS level') eq {level}"
    nf3 = f"col('Code {year}') eq ''"
    s = f"NUTS level {level}"
    p1 = Popen(["xan", "filter", f1, ALLLEVELS], stdout=PIPE)
    p2 = Popen(["xan", "filter", f2], stdin=p1.stdout, stdout=PIPE)
    p3 = Popen(["xan", "filter", "--invert-match", nf3], stdin=p2.stdout, stdout=PIPE)
    p4 = Popen(["xan", "select", s], stdin=p3.stdout, stdout=PIPE)
    output = p4.communicate()[0].decode().split('\n')[1:-1]
    return output

def getNutsLocations(country: str, format: str = 'dict', year: int = 2024):
    locsDict = {
        level: getNutsLocationsLevel(country, level, year)
        for level in LEVELS}
    if format == 'dict':
        return locsDict
    elif format == 'flatten':
        return [(loc, level) for level in locsDict for loc in locsDict[level]]
    else:
        raise ValueError(f"Format must be 'dict' or 'flatten'. Found {format}")

def getUnits(country: str | None = None, year: int = 2024):
    path = globals()[f"FLATTEN{year}"]
    with open(path, newline='') as csvfile:
        units = [d for d in csv.DictReader(csvfile)]
    if country:
        code = COUNTRYCODES[country]
        return [d for d in units if d['country_code'] == code]
    else:
        return units

def getCountryCode(code: str) -> str:
    return code[:2]

def getParentCode(code: str) -> str:
    return code[:-1]

def flattenNutsGenderDistributions(year: int = 2024) -> None:
    with open(NUTS3GENDERTOTAL) as tf:
        tD = [d for d in csv.DictReader(tf)]
    with open(NUTS3GENDERMALES) as mf:
        mD = [d for d in csv.DictReader(mf)]
    with open(NUTS3GENDERFEMALES) as ff:
        fD = [d for d in csv.DictReader(ff)]
    codes = [u['code'] for u in getUnits(year=year)]
    gDist = []
    for code in codes:
        gd = {'code': code, 'year': year}
        for m in mD:
            if m['code'] == code:
                try:
                    gd['male'] = strToInt(m[str(year)])
                except:
                    continue
        for f in fD:
            if f['code'] == code:
                try:
                    gd['female'] = strToInt(f[str(year)])
                except:
                    continue
        for t in tD:
            if t['code'] == code:
                try:
                    gd['total'] = strToInt(t[str(year)])
                except:
                    continue
        if len(gd) == 5:
            gDist.append(gd)
        else:
            print(f"No suitable gendre data found, skipping code {code}")

    outpath = globals()[f"NUTS3GENDERFLATTEN{year}"]
    with open(outpath, 'w', newline='') as csvfile:
        headers = ['total', 'code', 'female', 'year', 'male']
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in gDist:
            writer.writerow(row)
    print(f"Flatten file saved at {outpath}")

def getNutsGenderDistributions(country: str | None = None, year: int = 2024):
    path = globals()[f"NUTS3GENDERFLATTEN{year}"]
    with open(path, 'r') as csvfile:
        genderDistDicts = [d for d in csv.DictReader(csvfile)]
    if country:
        country_code = COUNTRYCODES[country]
        return [d for d in genderDistDicts if d['code'][:2] == country_code]
    else:
        return genderDistDicts

def getNutsAgeDistributions(country: str, year: int = 2024):
    age_categories = NUTS3AGECATS
    gender_categories = ["T", "F", "M"]
    country_code = COUNTRYCODES[country]
    file = f"/home/jimena/work/dev/SoMeCens/somecens/nuts/data/nuts_age_flatten_{country}_{year}.csv"

    dist = []
    country_code = COUNTRYCODES[country]
    with open(file, 'r') as csvfile:
        data = [d for d in csv.DictReader(csvfile) if d['code'][:2] == country_code]
    codes = {d['code'] for d in data}
    ageDist = []
    for code in codes:
        ageDist.append({
            'code': code,
            'year': year,
            'age_distributions': {
            d['age']: {
                'total': d['total'],
                'female': d['female'],
                'male': d['male']
            }
            for d in data if d['code'] == code}
        })
    return ageDist