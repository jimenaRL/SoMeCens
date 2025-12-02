#!/bin/bash

COUNTRY="chile"
STOPWORDS="el|la|lo|les|las|los|de|del|en"
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2020 \
    --unitspath=/home/jimena/work/dev/SoMeCens/data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=/home/jimena/work/dev/SoMeCens/data/chile/chile_metadata_epo_2020.csv \
    --stopwords=${STOPWORDS} && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2023 \
    --unitspath=/home/jimena/work/dev/SoMeCens/data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=/home/jimena/work/dev/SoMeCens/data/chile/chile_metadata_epo_2023.csv \
    --stopwords=${STOPWORDS} && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2025 \
    --unitspath=/home/jimena/work/dev/SoMeCens/data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=/home/jimena/work/dev/SoMeCens/data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=/home/jimena/work/dev/SoMeCens/data/chile/chile_metadata_epo_2025.csv \
    --stopwords=${STOPWORDS}
