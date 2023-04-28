# to clean, if required:
#rm neo/*summaries*
for file in neo/gloss*.json; do
  python link_summaries.py $file
done
