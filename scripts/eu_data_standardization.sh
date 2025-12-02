#!/bin/bash

declare -a COUNTRIES=(
    austria
    belgium
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

declare -a METADATAYEARS=(
    2020
    2023
    2025
)

NUTSYEAR=2024

for COUNTRY in ${COUNTRIES[@]}; do
    for YEAR in ${METADATAYEARS[@]}; do
        EPODBPATH=/mnt/hdd2/epodata/stage/20250929/pseudonymized_alldata/${COUNTRY}_${YEAR}_pseudonymized_alldata.db
        IDSDBPATH=/mnt/hdd2/epodata/stage/20250929/lut/${COUNTRY}_${YEAR}_lut.db
        if [[ -f "$EPODBPATH" ]]; then
            python scripts/eu_data_standardization.py \
                --metadatayear=${YEAR} \
                --nutsyear=${NUTSYEAR} \
                --country=${COUNTRY} \
                --epodbpath=${EPODBPATH}  \
                --idsdbpath=${IDSDBPATH}
        else
            echo "---------------------------------------------------------"
            echo "$EPODBPATH database does not exist"
        fi
    done
done
