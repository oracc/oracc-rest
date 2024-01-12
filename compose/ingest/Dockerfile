FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y jq

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest/ ./ingest/

CMD python3 -m ingest.bulk_upload --host http://elasticsearch:9200 ${ORACC_INGEST_DIRECTORY:-ingest/assets/dev/sample-glossaries}/*
