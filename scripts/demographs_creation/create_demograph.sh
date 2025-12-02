python scripts/create_demograph.py --country=czechia --metadatayear=2020 && \
python scripts/create_demograph.py --country=czechia --metadatayear=2023 && \

python scripts/create_demograph.py --country=denmark --metadatayear=2020 && \
python scripts/create_demograph.py --country=denmark --metadatayear=2023 && \

python scripts/create_demograph.py --country=estonia --metadatayear=2020 && \
python scripts/create_demograph.py --country=estonia --metadatayear=2023 && \

python scripts/create_demograph.py --country=ireland --metadatayear=2020 && \
python scripts/create_demograph.py --country=ireland --metadatayear=2023 && \

python scripts/create_demograph.py --country=greece --metadatayear=2020 && \
python scripts/create_demograph.py --country=greece --metadatayear=2023 && \

python scripts/create_demograph.py --country=cyprus --metadatayear=2020 && \
python scripts/create_demograph.py --country=cyprus --metadatayear=2023 && \

python scripts/create_demograph.py --country=latvia --metadatayear=2020 && \
python scripts/create_demograph.py --country=latvia --metadatayear=2023 && \

python scripts/create_demograph.py --country=lithuania --metadatayear=2020 && \
python scripts/create_demograph.py --country=lithuania --metadatayear=2023 && \

python scripts/create_demograph.py --country=hungary --metadatayear=2020 && \
python scripts/create_demograph.py --country=hungary --metadatayear=2023 && \

python scripts/create_demograph.py --country=malta --metadatayear=2020 && \
python scripts/create_demograph.py --country=malta --metadatayear=2023 && \

python scripts/create_demograph.py --country=portugal --metadatayear=2020 && \
python scripts/create_demograph.py --country=portugal --metadatayear=2023 && \

python scripts/create_demograph.py --country=romania --metadatayear=2020 && \
python scripts/create_demograph.py --country=romania --metadatayear=2023 && \

python scripts/create_demograph.py --country=slovenia --metadatayear=2020 && \
python scripts/create_demograph.py --country=slovenia --metadatayear=2023 && \

python scripts/create_demograph.py --country=slovakia --metadatayear=2020 && \
python scripts/create_demograph.py --country=slovakia --metadatayear=2023 && \

python scripts/create_demograph.py --country=finland --stopwords="suomi" --metadatayear=2020 && \
python scripts/create_demograph.py --country=finland --stopwords="suomi" --metadatayear=2023 && \

python scripts/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2020 && \
python scripts/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2023 && \
python scripts/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2025 && \

python scripts/create_demograph.py --country=austria --stopwords="in|aus" --metadatayear=2020 && \
python scripts/create_demograph.py --country=austria --stopwords="in|aus" --metadatayear=2023 && \

python scripts/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2020 && \
python scripts/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2023 && \
python scripts/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2025 && \

COUNTRY="belgium"
STOPWORDS="the|aan|de|en|op|van|le|la|les|las|de|des|à|au|aux|prov|stad|arr|region|vlaams|BE"
python scripts/create_demograph.py --country=${COUNTRY} --metadatayear=2020 --stopwords=${STOPWORDS} && \
python scripts/create_demograph.py --country=${COUNTRY} --metadatayear=2023 --stopwords=${STOPWORDS} && \
python scripts/create_demograph.py --country=${COUNTRY} --metadatayear=2025 --stopwords=${STOPWORDS} && \

python scripts/create_demograph.py \
    --country=luxembourg \
    --metadatayear=2020 \
    --stopwords="le|la|les|las|de|des|à|au|aux|sur" && \
python scripts/create_demograph.py \
    --country=luxembourg \
    --metadatayear=2023 \
    --stopwords="le|la|les|las|de|des|à|au|aux|sur" && \

python scripts/create_demograph.py \
    --country=netherlands \
    --metadatayear=2020 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \
python scripts/create_demograph.py \
    --country=netherlands \
    --metadatayear=2023 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \
python scripts/create_demograph.py \
    --country=netherlands \
    --metadatayear=2025 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \

python scripts/create_demograph.py \
    --country=spain \
    --metadatayear=2020 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \
python scripts/create_demograph.py \
    --country=spain \
    --metadatayear=2023 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \
python scripts/create_demograph.py \
    --country=spain \
    --metadatayear=2025 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \

python scripts/create_demograph.py \
    --country=italy \
    --metadatayear=2020 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \
python scripts/create_demograph.py \
    --country=italy \
    --metadatayear=2023 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \
python scripts/create_demograph.py \
    --country=italy \
    --metadatayear=2025 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \

python scripts/create_demograph.py \
    --country=germany \
    --metadatayear=2020 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \
python scripts/create_demograph.py \
    --country=germany \
    --metadatayear=2023 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \
python scripts/create_demograph.py \
    --country=germany \
    --metadatayear=2025 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \

python scripts/create_demograph.py \
    --country=france \
    --metadatayear=2020 \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \
python scripts/create_demograph.py \
    --country=france \
    --metadatayear=2023 \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \
python scripts/create_demograph.py \
    --country=france \
    --metadatayear=2025 \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \


COUNTRY="chile"
STOPWORDS="el|la|lo|les|las|los|de|del|en"
python scripts/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2020 \
    --unitspath=data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=data/chile/chile_metadata_2023.csv \
    --stopwords=${STOPWORDS} && \
python scripts/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2023 \
    --unitspath=data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=data/chile/chile_metadata_2023.csv \
    --stopwords=${STOPWORDS} && \
python scripts/create_demograph.py \
    --country=${COUNTRY} \
    --metadatayear=2025 \
    --unitspath=data/chile/chile_geounits_census_2024.csv \
    --subunitspath= \
    --genderdistpath=data/chile/chile_gender_distribution_census_2024.csv \
    --agedistpath=data/chile/chile_age_distribution_census_2024.csv \
    --usersdatapath=data/chile/chile_metadata_2023.csv \
    --stopwords=${STOPWORDS} && \

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
