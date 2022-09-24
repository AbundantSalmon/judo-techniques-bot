# syntax=docker/dockerfile:1
FROM python:3.10.7-slim-bullseye
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc
RUN pip install -r requirements/base.txt
CMD python -m judo_techniques_bot
