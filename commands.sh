python scripts/create_demograph.py \
    --country=netherlands \
    --stopwords="the|aan|de|en|op|van" \
    --debugcode=NL350

python scripts/create_demograph.py \
    --country=france \
    --stopwords="le|la|les|las|de|des|à|au|aux" \
    --debugcode=FRK21

python scripts/create_demograph.py \
    --country=spain \
    --stopwords="el|la|lo|les|las|los|de|en"

python scripts/create_demograph.py \
    --country=italy \
    --stopwords="di"

python scripts/create_demograph.py \
    --country=germany \
    --stopwords="in|aus"

python scripts/create_demograph.py \
    --country="United States" \
    --unitspath=data/us/us_geounits_year2023.csv \
    --subunitspath= \
    --genderdistpath=data/us/us_genre_distribution_year2023.csv \
    --agedistpath= \
    --usersdatapath=/home/jimena/work/dev/SoMeCens/data/us/us_metadata2023.csv \
    --debugcode=56039 \
    --stopwords='of|the|County'


python scripts/create_demograph.py \
    --country=luxembourg \
    --stopwords="la|sur" \
    --debugcode=LU000

python scripts/create_demograph.py \
    --country=romania
