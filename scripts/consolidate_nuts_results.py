import os
from glob import glob
from datetime import datetime
from argparse import ArgumentParser

from somecens.nuts.conf  import COUNTRYCODES

# Then upload consolidated data to https://gisco-services.ec.europa.eu/image/
# to produce cloropleths

BASEPATH = f"/mnt/hdd1/jimena/SoMeCens/exports/"

ap = ArgumentParser()
ap.add_argument('--year', type=int, required=True)

args = ap.parse_args()
year = args.year

resultsfolder = os.path.join(BASEPATH)
outfolder = os.path.join(BASEPATH, "nuts_consolidated")
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

        percpath = os.path.join(folder, f"nb_matchs_perc_{country}_nuts_2024_epo_{year}_level_{level}.csv")
        with open(percpath) as f:
            percdata.extend([l.replace('\n', '') for l in f.readlines()])

    outfile = os.path.join(outfolder, f"nb_matchs_perc_nuts_2024_epo_{year}_level_{level}.csv")
    with open(outfile, 'w') as f:
        f.writelines("\n".join(percdata) + "\n")
    print(f"Consolidated data saved at {outfile}")
    os.system(f"xan head {outfile} | xan v --no-headers")
