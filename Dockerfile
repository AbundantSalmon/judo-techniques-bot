# syntax=docker/dockerfile:1
FROM python:3.13.0-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get install -y libpq-dev gcc

RUN useradd -ms /bin/sh -u 1001 app
USER app

WORKDIR /app
COPY --chown=app:app . /app
RUN uv sync --locked

CMD ["uv", "run", "-m", "judo_techniques_bot"]
