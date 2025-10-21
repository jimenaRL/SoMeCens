import os
from glob import glob
from datetime import datetime

from somecens.nuts.conf  import COUNTRYCODES

# Then upload consolidated data to https://gisco-services.ec.europa.eu/image/
# to produce cloropleths

RESULTSDATE = datetime.today().strftime('%Y%m%d')
BASEPATH = f"/home/jimena/work/dev/SoMeCens/results"
RESULTSFOLDER = os.path.join(BASEPATH, RESULTSDATE)
OUTFOLDER = os.path.join(BASEPATH, RESULTSDATE, "nuts_consolidated")
os.makedirs(OUTFOLDER, exist_ok=True)

for level in [0, 1, 2, 3]:
    data = []
    percdata = []
    for country in COUNTRYCODES.keys():

        # skip missing data
        if country in ["bulgaria", "croatia"]:
            continue

        folder = os.path.join(RESULTSFOLDER, country)
        if not os .path.exists(folder):
            # print(f"Skipping country {country}. Dind't find folder {folder}")
            continue

        path = os.path.join(folder, f"nb_matchs_{country}_nuts_{level}.csv")
        with open(path) as f:
            data.extend([l.replace('\n', '') for l in f.readlines()])

        percpath = os.path.join(folder, f"nb_matchs_perc_{country}_nuts_{level}.csv")
        with open(percpath) as f:
            percdata.extend([l.replace('\n', '') for l in f.readlines()])

    outfile = os.path.join(OUTFOLDER, f"nuts_nb_matchs_level_{level}.csv")
    with open(outfile, 'w') as f:
        f.writelines("\n".join(data) + "\n")
    print(f"Consolidated data saved at {outfile}")
    os.system(f"xan head {outfile} | xan v --no-headers")

    outfile = os.path.join(OUTFOLDER, f"nuts_perc_matchs_level_{level}.csv")
    with open(outfile, 'w') as f:
        f.writelines("\n".join(percdata) + "\n")
    print(f"Consolidated data saved at {outfile}")
    os.system(f"xan head {outfile} | xan v --no-headers")
