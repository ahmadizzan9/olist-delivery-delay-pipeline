FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install dbt-postgres==1.8.0 "dbt-core==1.8.0"

WORKDIR /usr/app/dbt