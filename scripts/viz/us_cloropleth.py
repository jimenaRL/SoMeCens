# inspired from https://python-graph-gallery.com/choropleth-map-plotly-python/
import os
import json

import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# originally downloaded from https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json
USGEOJSONPATH = "data/us/geojson-counties-fips.json"
RESULTSFOLDER = "results/20251019/UnitedStates"
FILE = os.path.join(RESULTSFOLDER, "nb_matchs_perc_UnitedStates_nuts_2.csv")
OUTHTML = os.path.join(RESULTSFOLDER, "choropleth_nb_matchs_perc_UnitedStates_nuts_2.html")

# load the county boundary coordinates
with open(USGEOJSONPATH, 'r') as f:
    counties = json.load(f)

# load us users localized data
geounits = pd.read_csv(
    "data/us/us_geounits_year2023.csv",
    encoding="ISO-8859-1",
    dtype=str)[["code", "label"]]

df = pd.read_csv(FILE, dtype={"fips": str})
l = len(df)
df = df.merge(geounits, left_on="fips", right_on="code")
assert l == len(df)

# build the choropleth
fig = px.choropleth(df,
    geojson=counties,
    locations='fips',
    color='perc',
    color_continuous_scale="Viridis",
    range_color=(0, 12),
    scope="usa",
    hover_data="label",
    labels={'perc':'Percetage of localized users'},
    title="Percetage of US localized users per county",
)

fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

# Improve the legend
fig.update_layout(coloraxis_colorbar=dict(
    thicknessmode="pixels", thickness=10,
    lenmode="pixels", len=150,
    yanchor="top", y=0.8,
    ticks="outside", ticksuffix=" %",
    dtick=5
))

# save this file as a standalone html file
fig.write_html(OUTHTML)

fig.show()

# include it in a jupyter notebook with an iframe:
# %%html
# <iframe src=f"OUTHTML" width="800" height="600" title="Choropleth map with plotly" style="border:none"></iframe>
