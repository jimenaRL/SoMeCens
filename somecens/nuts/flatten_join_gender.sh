TMPFILE=$(mktemp)
TMPFILE2=$(mktemp)
OUTFILE=data/nuts3_gender_flatten.csv

xan join --prefix-left=male_ --prefix-right=female_ \
code data/NUTS123_Y2015_2024_Gender.xlsx\ -\ Sheet\ 2_Males.csv \
code data/NUTS123_Y2015_2024_Gender.xlsx\ -\ Sheet\ 3_Females.csv > "${TMPFILE}"

xan rename code,label -s male_code,male_label "${TMPFILE}" | \
xan drop female_code,female_label > "${TMPFILE2}"


xan join --prefix-right=total_ \
code "${TMPFILE2}" \
code data/NUTS123_Y2015_2024_Gender.xlsx\ -\ Sheet\ 1_Total.csv  | \
xan drop total_code,total_label > "${TMPFILE}"

for i in 1 2 3 4 5 6 7 8 9 10; do
  xan drop total_ "${TMPFILE}" > "${TMPFILE2}"
  mv "${TMPFILE2}" "${TMPFILE}"
  xan drop male_ "${TMPFILE}" > "${TMPFILE2}"
  mv "${TMPFILE2}" "${TMPFILE}"
  xan drop female_ "${TMPFILE}" > "${TMPFILE2}"
  mv "${TMPFILE2}" "${TMPFILE}"
done

mv "${TMPFILE}" "${OUTFILE}"

xan slice -l 3 "${OUTFILE}" | xan v

echo "File save at ${OUTFILE}"

