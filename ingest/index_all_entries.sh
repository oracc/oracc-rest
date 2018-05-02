# to clean the files, if required:
rm neo/*entries*

# to clean the ES databse, if required:
curl -XPOST 'localhost:9200/oracc/entry/_delete_by_query?conflicts=proceed&pretty' -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  }
}
'

for file in neo/gloss-???.json; do
  python break_down.py $file
done

for file in neo/*entries*; do
  curl -XPOST localhost:9200/oracc/entry/_bulk?pretty -H "Content-Type: application/x-ndjson" --data-binary "@$file"
done
