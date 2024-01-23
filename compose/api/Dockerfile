FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt && useradd -M oracc

COPY app.py /app/
COPY api/ /app/api/

USER oracc

CMD ["gunicorn", "--log-file=-", "--worker-tmp-dir", "/dev/shm", "--workers=2", "--threads=4", "--worker-class=gthread", "-b", "0.0.0.0:8000", "api:app"]
