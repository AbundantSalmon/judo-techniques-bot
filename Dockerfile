# syntax=docker/dockerfile:1
FROM python:3.11.4-slim-bullseye
RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /app
COPY requirements/base.txt requirements/base.txt
RUN pip install -r requirements/base.txt
COPY . /app
CMD python -m judo_techniques_bot
