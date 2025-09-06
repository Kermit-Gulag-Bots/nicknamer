FROM python:3.12.3-slim

RUN mkdir -p /app/data
WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/
RUN poetry install -n --no-root --only main

COPY *.py /app/
COPY data/* /app/data/

ENTRYPOINT exec poetry run python levi.py
