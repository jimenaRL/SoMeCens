python scripts/create_demograph.py --country=czechia && \
python scripts/create_demograph.py --country=denmark && \
python scripts/create_demograph.py --country=estonia && \
python scripts/create_demograph.py --country=ireland && \
python scripts/create_demograph.py --country=greece && \
python scripts/create_demograph.py --country=cyprus && \
python scripts/create_demograph.py --country=latvia && \
python scripts/create_demograph.py --country=lithuania && \
python scripts/create_demograph.py --country=hungary && \
python scripts/create_demograph.py --country=malta && \
python scripts/create_demograph.py --country=portugal && \
python scripts/create_demograph.py --country=romania && \
python scripts/create_demograph.py --country=slovenia && \
python scripts/create_demograph.py --country=slovakia && \
python scripts/create_demograph.py --country=finland --stopwords="suomi" && \
python scripts/create_demograph.py --country=sweden --stopwords="sverige|norrland" && \
python scripts/create_demograph.py --country=austria --stopwords="in|aus" && \
python scripts/create_demograph.py --country=poland --stopwords="makroregion" && \

python scripts/create_demograph.py \
    --country=belgium \
    --stopwords="BE,the|aan|de|en|op|van|le|la|les|las|de|des|à|au|aux|prov|stad|arr|region|vlaams" && \


python scripts/create_demograph.py \
    --country=france \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \

python scripts/create_demograph.py \
    --country=luxembourg \
    --stopwords="le|la|les|las|de|des|à|au|aux|sur" && \
python scripts/create_demograph.py \
    --country=netherlands \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \
python scripts/create_demograph.py \
    --country=spain \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \
python scripts/create_demograph.py \
    --country=italy \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \
python scripts/create_demograph.py \
    --country=germany \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt"
python scripts/create_demograph.py \
    --country="United States" \
    --unitspath=data/us/us_geounits_year2023.csv \
    --subunitspath= \
    --genderdistpath=data/us/us_genre_distribution_year2023.csv \
    --agedistpath= \
    --usersdatapath=/home/jimena/work/dev/SoMeCens/data/us/us_metadata2023.csv \
    --stopwords='of|the|county|district'