# inspired from https://python-graph-gallery.com/choropleth-map-plotly-python/
# tutorial at https://plotly.com/python/choropleth-maps/
#  https://www.bcn.cl/siit/mapas_vectoriales/index_html/

import os
import json

import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


# level = 3 # "comunas"
level = 1 # "regiones"

RESULTSFOLDER = "results/20251201/chile"

LEVELDATA = {
    1: {
        "geojsonpath": "/home/jimena/work/dev/Chile-GeoJSON/Regional.geojson",
        "geounitspath": "data/chile/chile_geounits_census_2024.csv",
        "file": os.path.join(RESULTSFOLDER, "nb_matchs_perc_chile_nuts_2024_epo_2023_level_1.csv"),
        "htmlpath": os.path.join(RESULTSFOLDER, "choropleth_nb_matchs_perc_chile_regiones.html"),
        "imagepath": os.path.join(RESULTSFOLDER, "choropleth_nb_matchs_perc_chile_regiones.png"),
        "idkey": 'codregion'

    },
    3: {
        "geojsonpath": "/home/jimena/work/dev/Chile-GeoJSON/comunas.geojson",
        "geounitspath": "data/chile/chile_geounits_census_2024.csv",
        "file": os.path.join(RESULTSFOLDER, "nb_matchs_perc_chile_nuts_2024_epo_2023_level_3.csv"),
        "htmlpath": os.path.join(RESULTSFOLDER, "choropleth_nb_matchs_perc_chile_comunas.html"),
        "imagepath": os.path.join(RESULTSFOLDER, "choropleth_nb_matchs_perc_chile_comunas.png"),
        "idkey": 'cod_comuna'

    }
}


# load the units boundary coordinates (geojson data)
with open(LEVELDATA[level]["geojsonpath"], 'r') as f:
    geojson = json.load(f)

for g in geojson['features']:
    g.update({'id': g['properties'][LEVELDATA[level]["idkey"]]})

# load us users localized data
geounits = pd.read_csv(
    LEVELDATA[level]["geounitspath"],
    dtype=str)[["code", "label"]]

df = pd.read_csv(
    LEVELDATA[level]["file"],
    names=['code', 'perc'],
    dtype={"code": str, "perc": float})
l = len(df)
df = df.merge(geounits, on="code")
assert l == len(df)

# build the choropleth
fig = px.choropleth(
    data_frame=df,
    geojson=geojson,
    locations='code',
    color='perc',
    color_continuous_scale="Viridis",
    range_color=(0, 1.5 * df.perc.describe()['mean']),
    scope="south america",
    hover_data="label",
    labels={'perc':'percetage of localized users'},
    title="Percetage of localized users",
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Improve the legend
fig.update_layout(
    coloraxis_colorbar=dict(
        thicknessmode="pixels",
        thickness=10,
        lenmode="pixels",
        len=350,
        yanchor="top",
        y=0.8,
        ticks="outside",
        ticksuffix=" %"
))

# save this file as a standalone html file
fig.write_image(LEVELDATA[level]["imagepath"])
print(f"Image saved at {LEVELDATA[level]["imagepath"]}")

fig.write_html(LEVELDATA[level]["htmlpath"])
print(f"Html saved at {LEVELDATA[level]["htmlpath"]}")


fig.show()

# include it in a jupyter notebook with an iframe:
print(f'%%html <iframe src=f"{LEVELDATA[level]["htmlpath"]}" width="800" height="600" title="Choropleth map with plotly" style="border:none"></iframe>')
