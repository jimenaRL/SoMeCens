python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=czechia --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=czechia --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=denmark --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=denmark --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=estonia --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=estonia --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=ireland --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=ireland --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=greece --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=greece --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=cyprus --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=cyprus --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=latvia --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=latvia --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=lithuania --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=lithuania --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=hungary --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=hungary --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=malta --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=malta --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=portugal --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=portugal --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=romania --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=romania --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=slovenia --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=slovenia --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=slovakia --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=slovakia --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=finland --stopwords="suomi" --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=finland --stopwords="suomi" --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2023 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=sweden --stopwords="sverige|norrland" --metadatayear=2025 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=austria --stopwords="in|aus" --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=austria --stopwords="in|aus" --metadatayear=2023 && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2020 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2023 && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=poland --stopwords="makroregion" --metadatayear=2025 && \

COUNTRY="belgium"
STOPWORDS="the|aan|de|en|op|van|le|la|les|las|de|des|à|au|aux|prov|stad|arr|region|vlaams|BE"
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=${COUNTRY} --metadatayear=2020 --stopwords=${STOPWORDS} && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=${COUNTRY} --metadatayear=2023 --stopwords=${STOPWORDS} && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py --country=${COUNTRY} --metadatayear=2025 --stopwords=${STOPWORDS} && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=luxembourg \
    --metadatayear=2020 \
    --stopwords="le|la|les|las|de|des|à|au|aux|sur" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=luxembourg \
    --metadatayear=2023 \
    --stopwords="le|la|les|las|de|des|à|au|aux|sur" && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=netherlands \
    --metadatayear=2020 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=netherlands \
    --metadatayear=2023 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=netherlands \
    --metadatayear=2025 \
    --stopwords="the|aan|de|en|op|van|agglomeratie" && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=spain \
    --metadatayear=2020 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=spain \
    --metadatayear=2023 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=spain \
    --metadatayear=2025 \
    --stopwords="el|la|lo|les|las|los|de|del|en|frontera" && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=italy \
    --metadatayear=2020 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=italy \
    --metadatayear=2023 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=italy \
    --metadatayear=2025 \
    --stopwords="di|dei|del|dell|all|della|nel|nellâ|in|Provincia Autonoma" && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=germany \
    --metadatayear=2020 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=germany \
    --metadatayear=2023 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=germany \
    --metadatayear=2025 \
    --stopwords="in|aus|am|der|stadtkreis|landeshauptstadt|landkreis|keisfreie|stadt|hansestadt" && \

python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=france \
    --metadatayear=2020 \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=france \
    --metadatayear=2023 \
    --stopwords="le|la|les|las|de|des|à|au|aux" && \
python /home/jimena/work/dev/SoMeCens/scripts/demographs_creation/create_demograph.py \
    --country=france \
    --metadatayear=2025 \
    --stopwords="le|la|les|las|de|des|à|au|aux"
