# Enke Systems Internship

PostgreSQL + Python tools (data generator, ETL, charts) running via Docker Compose.

## Services

- `postgres` — database, initialized from `init.sql`, always starts.
- `data_generator`, `etl`, `create_charts` — tools, profile `tools`, run on demand.

Config lives in `.env.user` (DB credentials, `NUM_CUSTOMERS`, `NUM_PRODUCTS`, `NUM_ORDERS`).

## Usage

```bash
# start the database
docker compose up -d postgres

# rebuild after code changes (docker compose run does NOT rebuild automatically)
docker compose build

# generate test data
docker compose --profile tools run --rm data_generator

# run ETL
docker compose --profile tools run --rm etl

# generate charts (saved to app/queries/charts)
docker compose --profile tools run --rm create_charts

# connect to the database
docker compose exec postgres psql -U postgres -d shop

# stop everything
docker compose down

# stop and wipe DB data
docker compose down -v
```
