FROM python:3.9-slim

RUN mkdir /app
WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml /app/
RUN poetry install -n --no-root --no-dev

COPY *.py /app/
COPY real_names.yaml /app/

RUN poetry run python nicknamer.py
