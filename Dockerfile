# Base image with common dependencies pre-installed once
FROM python:3.12-slim AS base
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Image for postgres
FROM postgres:16 AS postgres_image
COPY init.sql /docker-entrypoint-initdb.d/

# Image for data-generating
FROM base AS data_generator
COPY app ./app
CMD ["sh", "-c", "python -m app.main"]

# Image for create-charts
FROM base AS create_charts
COPY app ./app
CMD ["python", "-m", "app.queries.run"]

# Image for etl
FROM base AS etl
COPY app ./app
CMD ["python", "-m", "app.etl.pipelines_runner"]

# Image for tests
FROM base AS tests
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY app ./app
COPY tests ./tests
COPY pytest.ini .
CMD ["pytest"]
