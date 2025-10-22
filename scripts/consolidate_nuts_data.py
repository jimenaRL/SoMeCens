import os
from glob import glob
from datetime import datetime
from argparse import ArgumentParser

from somecens.nuts.conf  import COUNTRYCODES

# Then upload consolidated data to https://gisco-services.ec.europa.eu/image/
# to produce cloropleths

BASEPATH = f"/home/jimena/work/dev/SoMeCens/results"
DEFAULTDATE = datetime.today().strftime('%Y%m%d')

ap = ArgumentParser()
ap.add_argument('--date', type=str, default=DEFAULTDATE)

args = ap.parse_args()
date = args.date

resultsfolder = os.path.join(BASEPATH, date)
outfolder = os.path.join(BASEPATH, date, "nuts_consolidated")
os.makedirs(outfolder, exist_ok=True)

for level in [0, 1, 2, 3]:
    data = []
    percdata = []
    for country in COUNTRYCODES.keys():

        # skip missing data
        if country in ["bulgaria", "croatia"]:
            continue

        folder = os.path.join(resultsfolder, country)
        if not os .path.exists(folder):
            # print(f"Skipping country {country}. Dind't find folder {folder}")
            continue

        path = os.path.join(folder, f"nb_matchs_{country}_nuts_{level}.csv")
        with open(path) as f:
            data.extend([l.replace('\n', '') for l in f.readlines()])

        percpath = os.path.join(folder, f"nb_matchs_perc_{country}_nuts_{level}.csv")
        with open(percpath) as f:
            percdata.extend([l.replace('\n', '') for l in f.readlines()])

    outfile = os.path.join(outfolder, f"nuts_nb_matchs_level_{level}.csv")
    with open(outfile, 'w') as f:
        f.writelines("\n".join(data) + "\n")
    print(f"Consolidated data saved at {outfile}")
    os.system(f"xan head {outfile} | xan v --no-headers")

    outfile = os.path.join(outfolder, f"nuts_perc_matchs_level_{level}.csv")
    with open(outfile, 'w') as f:
        f.writelines("\n".join(percdata) + "\n")
    print(f"Consolidated data saved at {outfile}")
    os.system(f"xan head {outfile} | xan v --no-headers")
