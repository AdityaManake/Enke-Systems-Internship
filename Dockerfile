#image for postgres
FROM postgres:16 AS postgres_image
COPY init.sql /docker-entrypoint-initdb.d/



#image for data-generating
FROM python:3.12 AS data_generator
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["sh", "-c", "python -m app.main && python -m app.queries.run"]

#image for etl
FROM python:3.12 AS etl
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["python", "-m", "app.etl.etl_pipeline"]

