# Containerized PostgreSQL ETL & Analytics Pipeline

[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Pytest](https://img.shields.io/badge/Tested%20with-Pytest%20%26%20Testcontainers-green.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)

A production-grade, containerized ETL (Extract, Transform, Load) and analytical data processing project built with *
*Docker Compose**, **PostgreSQL 16**, and **Python**.

This repository provides an end-to-end data engine that simulates high-volume e-commerce transaction streams,
incrementally extracts operational OLTP data into materialized analytical reporting tables, verifies data integrity with
automated SQL set validation, benchmarks query performance, and renders visual analytics charts.

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Project Structure](#2-project-structure)
- [3. Prerequisites](#3-prerequisites)
- [4. Environment Setup](#4-environment-setup)
- [5. Running the Project](#5-running-the-project)
- [6. Docker Architecture](#6-docker-architecture)
- [7. ETL Pipeline Engine](#7-etl-pipeline-engine)
- [8. Testing & Quality Assurance](#8-testing--quality-assurance)
- [9. Charts & Performance Benchmarks](#9-charts--performance-benchmarks)
- [10. Troubleshooting](#10-troubleshooting)
- [11. Useful Commands Reference](#11-useful-commands-reference)

---

## 1. Project Overview

### Purpose

In enterprise application systems, querying large Online Transaction Processing (OLTP) databases for aggregate reports (
e.g., total sales by month, top revenue products) causes heavy CPU and disk I/O load, degrading core operational
performance.

This project solves that problem by building an incremental **ETL Pipeline** that reads transactional data, aggregates
metrics into an isolated `analytics` database schema, and materializes summary tables. Querying these materialized
tables speeds up analytical queries significantly compared to computing raw aggregations against millions of operational
rows.

### Overall Architecture

```
                   +---------------------------------------+
                   |          Docker Compose               |
                   |                                       |
                   |  +---------------------------------+  |
                   |  |      postgres (Container)       |  |
                   |  |  +---------------------------+  |  |
                   |  |  |  public schema (OLTP)     |  |  |
                   |  |  |  - customers, products    |  |  |
                   |  |  |  - orders, order_items    |  |  |
                   |  |  +---------------------------+  |  |
                   |  |  +---------------------------+  |  |
                   |  |  |  analytics schema (OLAP)  |  |  |
                   |  |  |  - materialized tables    |  |  |
                   |  |  |  - etl_metadata           |  |  |
                   |  |  +---------------------------+  |  |
                   |  +---------------+-----------------+  |
                   |                  ^                    |
                   |                  | (DB Connection)    |
   +---------------+------------------+--------------------+---------------+
   |               |                  |                    |               |
+--+------------+  |  +---------------+--+  +--------------+---+  +--------+-------+
|data_generator |  |  |       etl        |  |  create_charts   |  |     tests     |
|(Faker & ORM)  |  |  |(Incremental ETL) |  |(Matplotlib/Pandas|  |(Testcontainers|
+---------------+  |  +------------------+  +------------------+  +---------------+
```

1. **OLTP Layer (`public` schema)**: Pre-initialized with core relational tables: `customers`, `products`, `orders`, and
   `order_items`.
2. **Synthetic Data Generator (`data_generator`)**: Seeds configurable volumes of realistic transactions into the OLTP
   schema using Faker and SQLAlchemy bulk insertions.
3. **Incremental ETL Engine (`etl`)**: Extracts new or modified records created since the last run (`etl_metadata`),
   transforms raw transactions into business aggregates, upserts them into materialized tables under the `analytics`
   schema, and validates data consistency before committing.
4. **Analytics & Visualization (`create_charts`)**: Measures live execution time speedups between raw queries and
   materialized tables, exporting visual PNG charts.
5. **Isolated Integration Testing (`tests`)**: Uses Pytest and `testcontainers-python` to spin up disposable PostgreSQL
   16 containers directly via Docker Socket for reliable integration tests.

### Technology Stack

- **Database**: PostgreSQL 16
- **Programming Language**: Python 3.12
- **ORM & Database Driver**: SQLAlchemy 2.0+, psycopg2-binary
- **Data Processing & Visualization**: Pandas, Matplotlib, Faker
- **Testing**: Pytest, Testcontainers-python
- **Containerization**: Docker, Docker Compose (Multi-stage builds & profiles)

---

## 2. Project Structure

```
learn-docker/
├── Dockerfile                   # Multi-stage Docker build file for all services
├── docker-compose.yml           # Service orchestration and volume management
├── .env.example                 # Template environment variables
├── .env.user                    # Ignored local runtime environment credentials
├── init.sql                     # SQL script to initialize source OLTP database tables
├── pytest.ini                   # Pytest test suite runner configuration
├── requirements-dev.txt         # Dev dependencies for testing (pytest, testcontainers)
├── app/
│   ├── main.py                  # Entrypoint for synthetic data generator service
│   ├── database.py              # Database URL construction and engine utilities
│   ├── requirements.txt         # Production dependencies (SQLAlchemy, Faker, Pandas, Matplotlib)
│   ├── etl/                     # Core ETL Engine package
│   │   ├── analytics_schema.py  # DDL setup for analytics schema & target tables
│   │   ├── base_pipeline.py     # Abstract base class for incremental pipelines
│   │   ├── etl_metadata.py      # Tracking class for pipeline sync timestamps
│   │   ├── pipelines_runner.py  # Main runner managing pipeline execution & transactions
│   │   ├── validate_pipelines.py# Validation suite comparing raw SQL against materialized data
│   │   └── pipelines/           # Individual analytical pipeline modules
│   │       ├── average_order_value_pipeline.py
│   │       ├── customers_with_many_orders_pipeline.py
│   │       ├── most_expensive_order_per_customer_pipeline.py
│   │       ├── orders_per_month_pipeline.py
│   │       ├── top_customers_pipeline.py
│   │       └── top_products_pipeline.py
│   ├── models/                  # SQLAlchemy ORM model declarations
│   │   ├── customer.py
│   │   ├── order.py
│   │   ├── order_items.py
│   │   └── product.py
│   └── queries/                 # Visualization & benchmarking engine
│       ├── run.py               # Benchmarks query speeds and renders charts
│       └── charts/              # Output directory for generated chart images
└── tests/                       # Automated integration tests
    ├── conftest.py              # Test fixtures and Testcontainers setup
    └── test_pipelines_runner.py # Integration test cases (happy path, rollback, incremental)
```

---

## 3. Prerequisites

Ensure you have the following software installed on your host system:

- **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** (v24.0+ recommended) or Docker Engine & CLI.
- **[Docker Compose](https://docs.docker.com/compose/)** (v2.20+ included with Docker Desktop).
- **[Git](https://git-scm.com/)** for cloning the repository.
- *(Optional)* **Python 3.12+** if you wish to inspect or run code locally without containers orelse setup a venv.

---

## 4. Environment Setup

### Environment Files Explanation

- **`.env.user` (Git-Ignored)**: Stores user-specific credentials, local database settings, and data generation sizes.
  Because `.env.user` is listed in `.gitignore`, your credentials and local configurations are never committed to
  version control.
- **`.env.example` (Version-Controlled)**: Serves as a template file documenting all environment variables required by
  Docker Compose and Python scripts.

### Creating Your Configuration

To create your local environment file, copy `.env.example` to `.env.user`:

```bash
cp .env.example .env.user
```

### Environment Variables Glossary

| Environment Variable | Description                                          | Example / Default Value |
|:---------------------|:-----------------------------------------------------|:------------------------|
| `POSTGRES_DB`        | Name of the PostgreSQL target database               | `userdb`                |
| `POSTGRES_USER`      | Username for the PostgreSQL database superuser       | `abc`                   |
| `POSTGRES_PASSWORD`  | Password for the PostgreSQL database superuser       | `test123`               |
| `POSTGRES_HOST`      | Database host (use `postgres` within Docker network) | `postgres`              |
| `POSTGRES_PORT`      | Port exposed inside container network                | `5432`                  |
| `NUM_CUSTOMERS`      | Number of synthetic customer records to generate     | `10000`                 |
| `NUM_PRODUCTS`       | Number of synthetic product items to generate        | `1000`                  |
| `NUM_ORDERS`         | Number of synthetic orders to generate               | `100000`                |

---

## 5. Running the Project

Follow these step-by-step commands to run the complete pipeline lifecycle.

### Step 1: Start PostgreSQL Database

Start the database container in detached background mode:

```bash
docker compose up -d postgres
```

*Explanation*: Builds the database image (incorporating `init.sql`), starts PostgreSQL, exposes host port `5435` mapped
to container port `5432`, and initiates background health checks.

### Step 2: Generate Sample Data

Populate the database with synthetic OLTP transactions:

```bash
docker compose --profile tools run --rm data_generator
```

*Explanation*: Starts the `data_generator` container using the `tools` profile. It waits for PostgreSQL to become
healthy, then uses `Faker` to bulk-insert customer, product, and order data according to `.env.user` configuration. The
`--rm` flag removes the container upon completion.

### Step 3: Run the ETL Pipeline

Extract data and populate materialized analytics tables:

```bash
docker compose --profile tools run --rm etl
```

*Explanation*: Initializes the `analytics` schema (if not existing), executes all 6 ETL pipelines incrementally inside a
single database transaction, runs verification tests against raw tables, updates `analytics.etl_metadata`, and commits
changes.

### Step 4: Create Charts & Performance Benchmarks

Compare execution speeds and export visual charts:

```bash
docker compose --profile tools run --rm create_charts
```

*Explanation*: Benchmarks execution time between raw aggregation queries and materialized analytics tables, outputs
speedup statistics, and saves PNG images into `./app/queries/charts/`.

### Step 5: Run Specific ETL Pipelines

To execute only specific pipelines instead of the full suite, pass the pipeline names as arguments:

```bash
docker compose --profile tools run --rm etl python -m app.etl.pipelines_runner top_products orders_per_month
```

*Explanation*: Overrides the default container CMD and passes positional arguments to `pipelines_runner.py`. Valid
choices are: `orders_per_month`, `top_products`, `top_customers`, `customers_with_many_orders`,
`most_expensive_order_per_customer`, `avg_order_value`.

### Step 6: Run Integration Tests

Execute the automated test suite using Testcontainers:

```bash
docker compose --profile tools run --rm tests
```

*Explanation*: Mounts `/var/run/docker.sock` into the container to allow `testcontainers-python` to dynamically launch
an isolated PostgreSQL container and execute all Pytest scenarios.

### Step 7: Connect to PostgreSQL

Access the database interactively using `psql`:

```bash
docker compose exec postgres psql -U aditya -d userdb
```

*Explanation*: Executes an interactive shell session inside the running `postgres` container. You can query tables
directly (e.g., `SELECT * FROM analytics.top_products;`).

### Step 8: View Logs

Stream real-time output logs for troubleshooting:

```bash
docker compose logs -f postgres
```

*Explanation*: Displays and streams live stdout/stderr logs from the PostgreSQL container.

### Step 9: Stop Containers

Stop running background containers gracefully:

```bash
docker compose down
```

*Explanation*: Stops and removes containers and network bridges created by Docker Compose, preserving volume data.

### Step 10: Wipe Volume & Data Reset

To completely purge persistent database volumes:

```bash
docker compose down -v
```

*Explanation*: Stops containers and permanently deletes the named volume `postgres_data`, returning the database to an
empty state.

---

## 6. Docker Architecture

The project utilizes Docker Compose profiles to isolate background services from on-demand developer CLI tools:

| Service Name         | Profile     | Build Stage Target | Purpose & Function                                                                                                                                              |
|:---------------------|:------------|:-------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **`postgres`**       | *(Default)* | `postgres_image`   | Persistent PostgreSQL 16 database server. Loads `init.sql` on first boot, runs health checks via `pg_isready`, and persists data to volume `postgres_data`.     |
| **`data_generator`** | `tools`     | `data_generator`   | One-shot tool that generates synthetic customer, product, order, and order item records using Faker & SQLAlchemy.                                               |
| **`etl`**            | `tools`     | `etl`              | One-shot tool that runs `PipelinesRunner`, executing incremental ETL transformations, data validations, and metadata timestamp updates.                         |
| **`create_charts`**  | `tools`     | `create_charts`    | One-shot tool that benchmarks raw SQL queries against materialized analytics tables and generates PNG visual charts into host directory `./app/queries/charts`. |
| **`tests`**          | `tools`     | `tests`            | Integration test runner containing `pytest` and `requirements-dev.txt`. Mounts Docker socket to instantiate Testcontainers.                                     |

---

## 7. ETL Pipeline Engine

### Source Tables (OLTP)

The core database tables defined in `init.sql` store raw transactions:

- `customers` (id, email, name, created_at, updated_at)
- `products` (id, name, price, created_at, updated_at)
- `orders` (id, customer_id, ordered_at, created_at)
- `order_items` (id, order_id, product_id, quantity, total_price, created_at, updated_at)

### Incremental Processing Mechanics

Rather than recalculating entire datasets on every run (which degrades performance over time), each pipeline subclasses
`BasePipeline` and tracks execution timestamps:

1. **Timestamp Check**: Queries `analytics.etl_metadata` for `last_sync_time` registered for that specific pipeline.
2. **Filtered Extraction**: Filters source records using `WHERE :last_sync IS NULL OR created_at > :last_sync`.
3. **Atomic Upsert**: Performs `INSERT ... ON CONFLICT (primary_key) DO UPDATE` to update materialized metrics
   incrementally.
4. **Sync Persistence**: Updates `analytics.etl_metadata` with `MAX(created_at)` from source tables processed during the
   run.

```sql
INSERT INTO analytics.top_products (product_id, product_name, total_revenue)
SELECT p.id AS product_id, p.name AS product_name, CAST(SUM(oi.total_price) AS DECIMAL(18,3)) AS total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
WHERE :last_sync IS NULL OR oi.created_at > :last_sync
GROUP BY p.id, p.name
ON CONFLICT (product_id) DO UPDATE
    SET total_revenue = analytics.top_products.total_revenue + EXCLUDED.total_revenue;
```

### Materialized Analytics Tables

Aggregations are stored in the `analytics` schema:

- `analytics.orders_per_month`: Monthly aggregate order volumes.
- `analytics.top_products`: Total revenue generated per product.
- `analytics.top_customers`: Total monetary spend per customer.
- `analytics.customers_with_many_orders`: Total orders per customer.
- `analytics.most_expensive_order_per_customer`: Peak order amount per customer.
- `analytics.avg_order_value`: Order count, total spend, and calculated average order value per customer.

### Automated Validation & Set Comparison

To prevent corrupted calculations from reaching analytical layers, each pipeline implements validation using SQL set
operations (`EXCEPT` and `UNION ALL`). The system compares the data in `analytics.<table_name>` against live
calculations from `raw_query()`:

```sql
SELECT EXISTS (
    (SELECT * FROM analytics.top_products EXCEPT <raw_query>)
    UNION ALL
    (<raw_query> EXCEPT SELECT * FROM analytics.top_products)
);
```

If `EXISTS` returns `TRUE`, a data mismatch is present, and a `ValueError` is thrown.

### Transactional Atomicity & Rollback

All pipelines are wrapped inside a single database transaction in `PipelinesRunner`:

```python
with self.engine.begin() as conn:
    for pipeline_cls in self.pipeline_classes:
        pipeline = self._build_pipeline(pipeline_cls, conn)
        pipeline.run()  # execute -> validate -> update_sync_time
```

If any pipeline raises a validation or execution error, SQLAlchemy immediately rolls back the entire database
transaction. No partial updates or corrupted analytics metrics are committed.

---

## 8. Testing & Quality Assurance

### Framework Overview

The project employs **Pytest** alongside **Testcontainers-python**. Tests run completely isolated from your development
PostgreSQL instance.

### Testcontainers Workflow

When running `docker compose --profile tools run --rm tests`:

1. Testcontainers connects to host Docker daemon via `/var/run/docker.sock`.
2. Spins up an ephemeral, lightweight `postgres:16` container on a random port.
3. Automatically executes database DDL schema initialization (`Base.metadata.create_all` and `create_analytics_schema`).
4. Runs pytest test cases.
5. Destroys the ephemeral container upon completion.

### Test Scenarios Covered

Located in `tests/test_pipelines_runner.py`:

1. **`test_happy_path`**: Verifies end-to-end execution of all pipelines against seeded source data, ensuring row counts
   in materialized tables match expected counts and metadata is correctly recorded.
2. **`test_transaction_rollback`**: Uses `monkeypatch` to inject a validation failure into `TopProductsPipeline`.
   Verifies that the entire transaction is rolled back, leaving all `analytics.*` tables completely empty.
3. **`test_repeated_incremental_execution`**: Verifies incremental logic. Runs pipelines once, inserts new source
   transactions, re-runs pipelines, and asserts that updated table metrics reflect new revenue without duplicating
   baseline records.

---

## 9. Charts & Performance Benchmarks

Running `create_charts` executes `app/queries/run.py`, comparing live query execution times between un-indexed raw
source joins vs. materialized analytics tables.

### Benchmark Output & Speedups

The process logs query timing and speedup factors directly to stdout:

```
INFO - customer_vs_amount: raw=1.6409s materialized=0.1275s speedup=12.9x
INFO - product_vs_revenue: raw=0.1870s materialized=0.0041s speedup=46.0x
INFO - orders_per_month: raw=0.1346s materialized=0.0012s speedup=111.8x
```

### Exported PNG Charts

Chart files are saved directly into `./app/queries/charts/`:

| Chart File                               | Metric Visualized                      | Chart Type |
|:-----------------------------------------|:---------------------------------------|:-----------|
| `customer_vs_amount_*.png`               | Top 10 Customers by Total Spend        | Bar Chart  |
| `product_vs_revenue_*.png`               | Top 10 Products by Total Revenue       | Bar Chart  |
| `orders_per_month_*.png`                 | Order Volume per Month                 | Line Chart |
| `customer_vs_ordercount_*.png`           | Top Customers by Order Volume          | Bar Chart  |
| `mostexpensive_order_per_customer_*.png` | Top 20 Most Expensive Single Orders    | Line Chart |
| `ordervalue_vs_customers_*.png`          | Average Order Value (AOV) per Customer | Bar Chart  |

---

## 10. Troubleshooting

### 1. Code changes not taking effect (Docker image not rebuilding)

- **Cause**: `docker compose run` does not automatically rebuild Docker images when source files are edited.
- **Solution**: Force a rebuild prior to running commands:
  ```bash
  docker compose build
  # Or use --build flag directly:
  docker compose --profile tools run --build --rm etl
  ```

### 2. PostgreSQL Connection Failures

- **Cause**: The PostgreSQL container is still performing initial setup or initialization scripts.
- **Solution**: Check service health using `docker compose ps`. Wait for `(healthy)` status before launching dependent
  services.

### 3. Missing `.env.user` File

- **Cause**: Running containers without creating `.env.user`.
- **Solution**: Execute `cp .env.example .env.user` and verify credentials.

### 4. Container exits immediately with status code `0`

- **Cause**: Tool services (`data_generator`, `etl`, `create_charts`, `tests`) are designed as short-lived tasks that
  run once and exit.
- **Solution**: This is expected behavior. View logs using `docker compose logs <service_name>`.

### 5. Volume data corruption or stale schema

- **Cause**: Old database schemas persist inside the Docker volume across modifications to `init.sql`.
- **Solution**: Wipe the volume and rebuild:
  ```bash
  docker compose down -v
  docker compose up -d postgres
  ```

### 6. PostgreSQL Port Conflict

**Cause:**  If another application is already using port `5435` on your machine, Docker will be unable to bind the
PostgreSQL container to that port. As a result, you may not be able to connect to the database from your preferred
database client or application.

**Solution:**  Update the port mapping in `docker-compose.yml` to an available port, for example:

ports: 5436:5432, etc.

### 7. Full Project Reset Command

To completely clean up and restart the project from scratch:

  ```bash
  docker compose down -v --remove-orphans
  docker compose build --no-cache
  cp .env.example .env.user
  docker compose up -d postgres
```

---

## 11. Useful Commands Reference

| Task / Operation                 | Command                                                                                          |
|:---------------------------------|:-------------------------------------------------------------------------------------------------|
| **Start Database**               | `docker compose up -d postgres`                                                                  |
| **Build/Rebuild Images**         | `docker compose build`                                                                           |
| **Generate Sample Data**         | `docker compose --profile tools run --rm data_generator`                                         |
| **Run All ETL Pipelines**        | `docker compose --profile tools run --rm etl`                                                    |
| **Run Specific ETL Pipeline**    | `docker compose --profile tools run --rm etl python -m app.etl.pipelines_runner <pipeline_name>` |
| **Generate Charts & Benchmarks** | `docker compose --profile tools run --rm create_charts`                                          |
| **Execute Integration Tests**    | `docker compose --profile tools run --rm tests`                                                  |
| **Interactive Postgres Shell**   | `docker compose exec postgres psql -U aditya -d userdb`                                          |
| **Stream Postgres Logs**         | `docker compose logs -f postgres`                                                                |
| **Check Container Status**       | `docker compose ps`                                                                              |
| **Stop All Services**            | `docker compose down`                                                                            |
| **Stop & Wipe All Data**         | `docker compose down -v`                                                                         |
