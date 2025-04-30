import csv

from somecens.nuts.conf  import \
    COUNTRYCODES, \
    CODESCOUNTRY, \
    RENAMECOLUMNS, \
    NUTSPATH

RENAMECOLUMNS = {
    "Country Code": "country_code",
    "Code 2024": "code",
    "NUTS level 1": "level_1",
    "NUTS level 2": "level_2",
    "NUTS level 3": "level_3",
    "NUTS level": "level"
}

COLUMNS = [
    "country_code",
    "code",
    "level",
    "parent_code",
    "name"
]


with open(f'nuts_flatten.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=COLUMNS)
    writer.writeheader()
    with open(NUTSPATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for r in reader:
            tmp = {v: r[k] for k,v in RENAMECOLUMNS.items()}
            if tmp["level"] == '0':
                tmp["name"] = CODESCOUNTRY[tmp["code"]]
                tmp["parent_code"] = ''
            else:
                tmp["name"] = tmp[f"level_{tmp['level']}"]
                tmp["parent_code"] = tmp["code"][:-1]
            del tmp["level_1"]
            del tmp["level_2"]
            del tmp["level_3"]
            writer.writerow(tmp)

