FROM python:3.12.3-slim

RUN mkdir /app
WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/
RUN poetry install -n --no-root --only main

COPY *.py /app/
COPY real_names.yaml /app/

ENTRYPOINT poetry run python nicknamer.py
