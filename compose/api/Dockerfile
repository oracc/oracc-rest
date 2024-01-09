FROM python:3.9-slim-buster

WORKDIR /app

COPY ./requirements.txt /app

RUN pip install -r requirements.txt

COPY app.py /app/
COPY api/ /app/api/

CMD ["flask", "--app", "app", "--debug", "run", "--host", "0.0.0.0", "--port", "8000"]
