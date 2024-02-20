FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y jq && useradd -M oracc

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest/ ./ingest/

USER oracc

CMD python3 -m ingest.bulk_upload --wait 45 --host http://elasticsearch:9200 /glossaries/*.json
