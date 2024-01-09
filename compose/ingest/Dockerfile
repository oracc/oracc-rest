FROM python:3.8

WORKDIR /app

RUN apt-get update && apt-get install -y jq

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ingest/ ./ingest/

CMD ["python3", "-m", "ingest.bulk_upload", "--glob", "ingest/assets/dev/sample-glossaries/*"]
