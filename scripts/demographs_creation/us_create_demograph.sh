python scripts/create_demograph.py \
    --country="us" \
    --metadatayear=2020 \
    --unitspath=data/us/us_geounits_year2023.csv \
    --subunitspath= \
    --genderdistpath=data/us/us_genre_distribution_year2023.csv \
    --agedistpath=data/us/us_age_distribution_year2023.csv \
    --usersdatapath=data/us/us_metadata2023.csv \
    --stopwords='of|the|county|district' \
    --ignoreErrors && \
python scripts/create_demograph.py \
    --country="us" \
    --metadatayear=2023 \
    --unitspath=data/us/us_geounits_year2023.csv \
    --subunitspath= \
    --genderdistpath=data/us/us_genre_distribution_year2023.csv \
    --agedistpath=data/us/us_age_distribution_year2023.csv \
    --usersdatapath=data/us/us_metadata2023.csv \
    --stopwords='of|the|county|district' \
    --ignoreErrors && \
python scripts/create_demograph.py \
    --country="us" \
    --metadatayear=2025 \
    --unitspath=data/us/us_geounits_year2023.csv \
    --subunitspath= \
    --genderdistpath=data/us/us_genre_distribution_year2023.csv \
    --agedistpath=data/us/us_age_distribution_year2023.csv \
    --usersdatapath=data/us/us_metadata2023.csv \
    --stopwords='of|the|county|district' \
    --ignoreErrors
