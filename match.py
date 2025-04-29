import os
import csv
import yaml
import tempfile
from argparse import ArgumentParser

from somecens.conf import COUNTRYEARS, DEFAULTDB, DEFAULTDBPATTERN, METADATAFIELDS, NUTSLEVELS
from somecens.tools import getLastRelease, getLocations, getMetadata, writeCsv

def matchs(dbpath, outputpath):
    counts = {level: {} for level in NUTSLEVELS}
    locations = getLocations(country, format='flatten')
    metadata = getMetadata(dbpath)
    # write metadata and locations to tmp files
    with tempfile.NamedTemporaryFile() as tmpMeta:
        writeCsv(tmpMeta.name, metadata, headers=METADATAFIELDS)
        with tempfile.NamedTemporaryFile() as tmpLoc:
            writeCsv(tmpLoc.name, locations, headers=['name', 'level'])
            with tempfile.NamedTemporaryFile() as tmp:
                command = ' '.join([
                    "xan",
                    "regex-join",
                    "-i",
                    "--left",
                    "--parallel",
                    "description",
                    tmpMeta.name,
                    "name",
                    tmpLoc.name,
                    "--prefix-right",
                    "match_description_",
                    ">",
                    tmp.name
                ])
                os.system(command)
                command = ' '.join([
                    "xan",
                    "regex-join",
                    "-i",
                    "--left",
                    "--parallel",
                    "location",
                    tmp.name,
                    "name",
                    tmpLoc.name,
                    "--prefix-right",
                    "match_location_",
                    ">",
                    outputpath
                ])
                os.system(command)
                print(f"Csv file saved at {outputpath}")

if __name__ == "__main__":

    ap = ArgumentParser()
    ap.add_argument('--country', type=str, default=None, required=False)
    ap.add_argument('--year', type=str, default=None, required=False)
    ap.add_argument('--dbtype', type=str, default=DEFAULTDB, required=False)
    ap.add_argument('--dbpattern', type=str, default=DEFAULTDBPATTERN, required=False)
    ap.add_argument('--output', type=str, default='nutsMatchs', required=False)

    args = ap.parse_args()
    country = args.country
    year = args.year
    dbtype = args.dbtype
    dbpattern = args.dbpattern
    output = args.output

    if not (country and year):
        country_years = COUNTRYEARS
    else:
        country_years = {year: [country]}

    for year in country_years:
        for country in country_years[year]:
            filepath = f'{output}/{country}_{year}.csv'
            dbpath = getLastRelease(dbpattern, dbtype, country, year)
            matchs(dbpath, filepath)
            os.system(
                f"xan filter \"match_description_level ne '' ||  match_location_level ne ''\" {filepath} | xan v")
            print("Number of matchs found:")
            os.system(
                f"xan filter \"match_description_level ne '' ||  match_location_level ne ''\" {filepath} | xan count")
