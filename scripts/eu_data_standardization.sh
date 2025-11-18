#!/bin/bash

declare -a COUNTRIES=(
    austria
    belgium
    bulgaria
    cyprus
    czechia
    denmark
    estonia
    finland
    france
    germany
    greece
    hungary
    ireland
    italy
    latvia
    lithuania
    luxembourg
    malta
    netherlands
    poland
    portugal
    romania
    slovakia
    slovenia
    spain
    sweden
)

for COUNTRY in ${COUNTRIES[@]}; do
    python scripts/eu_data_standardization.py  --metadatayear=2023 --nutsyear=2024 --country=${COUNTRY} --epodbpath=/mnt/hdd2/epodata/stage/20250929/pseudonymized_alldata/${COUNTRY}_2023_pseudonymized_alldata.db
done
