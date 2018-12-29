FROM python:3.6-alpine

WORKDIR /app

COPY dev-requirements.txt /app/dev-requirements.txt
RUN pip install -U pip -r dev-requirements.txt

COPY . /app/
