spin up the application by running the following command from the top level directory of this repo:

docker-compose up --build

Send a basic request to elasticsearch from the terminal:

```
curl -X POST "your_elasticsearch_endpoint/your_index_name/_search" -H 'Content-Type: application/json' -d '{
  "query": {
    "match_all": {}
  }
}'
```
