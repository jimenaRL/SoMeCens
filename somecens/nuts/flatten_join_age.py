import concurrent
import pandas as pd
from somecens.nuts.conf import \
    NUTS3AGE20_74, \
    NUTS3AGEunder19, \
    NUTS3AGE75plus, \
    NUTS3AGECATS

country = 'france'
country_code = COUNTRYCODES[country]
year = 2024


def flatten(path, N):

    print(f"{N} {path}")

    df = pd.read_excel(path, sheet_name=f"Sheet {N}")

    genre = df.iloc[4, 2].split("[")[-1].split("]")[0]
    age = df.iloc[6, 2].split("[")[-1].split("]")[0][1:]
    # remove _ in _LT5 and _GE85
    if age[0] == '_':
        age = age[1:]

    df.iloc[9, 3:] = df.iloc[8, 3:]
    df.iloc[9] = df.iloc[9].fillna('NAN')
    df.columns = df.iloc[9]
    df = df.iloc[10:2151]
    df = df \
        .reset_index(inplace=False) \
        .drop(columns=["index", "NAN"]) \
        .rename(columns={"GEO (Codes)": "code", "GEO (Labels)": "label"})

    df = df[df.code.apply(lambda c: c[:2] == country_code)]
    df = df[["code", "label", str(year)]]
    df = df.rename(columns={str(year): genre})
    df = df.assign(age=age)

    return df, genre, age


jobs = [(NUTS3AGE20_74, N) for N in range(1, 34)]
jobs += [(NUTS3AGE75plus, N) for N in range(1, 15)]
jobs += [(NUTS3AGEunder19, N) for N in range(1, 13)]

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(flatten, j[0], j[1]) for j in jobs]
    results = [f.result() for f in futures]

ageData = {age: [r[0] for r in results if r[2] == age] for age in NUTS3AGECATS}

finaldf = pd.concat([
    ageData[age][0]
    .merge(ageData[age][1], on=['code', 'label', 'age'])
    .merge(ageData[age][2], on=['code', 'label', 'age'])
    for age in NUTS3AGECATS])

finaldf.rename(columns={
    'F': "female",
    'M': "male",
    'T': "total",
})

filepath = f"somecens/nuts/data/nuts_age_flatten_{country}_{year}.csv"
finaldf.to_csv(filepath, index=False)
print(f"Csv file saved at {filepath}")
