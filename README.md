# Social Media Census project 🌎📊

## SomeCens package could be use to:

- Create a Demograph tree object representing a country and its hierarchical organized geographic units 🌐
- Load sociodemographic (age and gender) information for units 👶👧👵👦🧔👴
- Localize user in units 📌
- Create choropleth maps to show sociodemographic and localisation data 🗺️
- Export tables with localized user and units sociodemographic data 📊

## 📊 Currently used with data from 
| Country | Census |
| ------------- | ------ |
| 🇪🇺 EU countries | [NUTS 2024 classification](https://ec.europa.eu/eurostat/web/nuts) |
| 🇨🇱 Chile | [2024 Census](https://censo2024.ine.gob.cl/estadisticas/) |
| 🇺🇸 USA | [2023 Annual County Resident Population Estimate](https://www.census.gov/) |

Check the provided [scripts](https://github.com/jimenaRL/SoMeCens/tree/0fddfc2ff01611bf9f21af2a36b2e648b1e2bbd2/scripts) for data formatting.

## 📊 Example of Europe 2024 NUTS level 3 coverage with [EPO](http://ramaciotti.org/projects/project-2021-10-EPO/) data

 ![Percent of users matched by SoMeCens project in NUTS3 Europe geographical units](nb_matchs_perc_nuts_3.png)

 Image made with IMAGE [web-tool](https://gisco-services.ec.europa.eu/image/) from the Geographic Information System of the European Commission ([GISCO](https://ec.europa.eu/eurostat/web/gisco)).

## 📊 Example of Chile 2024 Census comunas coverage with [EPO](http://ramaciotti.org/projects/project-2021-10-EPO/) data

<!-- choropleth_nb_matchs_perc_chile_comunas.html -->
<iframe 
  src="https://github.com/jimenaRL/jimenarl.github.io/blob/master/choropleth_nb_matchs_perc_chile_comunas.html" 
  width="100%" 
  height="600px" 
  title="Chile's comunas" 
  sandbox="allow-scripts"  <!-- Allows the embedded HTML to run scripts -->
></iframe>
