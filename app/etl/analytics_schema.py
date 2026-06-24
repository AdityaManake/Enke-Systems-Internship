from app.database import build_database_url
from sqlalchemy import create_engine, text


def main():
    engine = create_engine(build_database_url())
    create_analytics_schema(engine)


def create_analytics_schema(engine):
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE SCHEMA IF NOT EXISTS analytics;"
            )
        )

        conn.execute(
            text("""
                 CREATE TABLE IF NOT EXISTS analytics.etl_metadata
                 (
                     table_name
                     VARCHAR
                 (
                     100
                 ) PRIMARY KEY,
                     last_sync_time TIMESTAMP );
                 """)
        )

        conn.execute(
            text("""
                 CREATE TABLE IF NOT EXISTS analytics.orders_per_month
                 (
                     month
                     DATE
                     PRIMARY
                     KEY,
                     total_orders
                     BIGINT
                     NOT
                     NULL
                 );
                 """)
        )
