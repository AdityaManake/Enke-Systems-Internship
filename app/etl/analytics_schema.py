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
                     last_sync_time TIMESTAMPTZ );
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

        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS analytics.top_products
                          (
                              product_id
                              INT
                              PRIMARY
                              KEY,
                              product_name
                              VARCHAR
                          (
                              50
                          )
                              NOT
                              NULL,
                              total_revenue DECIMAL
                          (
                              18,
                              3
                          )
                              NOT
                              NULL

                              )
                          """))

        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS analytics.top_customers
                          (
                              customer_id
                              INT
                              PRIMARY
                              KEY,
                              customer_name
                              VARCHAR
                          (
                              50
                          ) NOT NULL,
                              total_amount_spend DECIMAL
                          (
                              18,
                              3
                          ) NOT NULL

                              )
                          """))

        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS analytics.customers_with_many_orders
                          (
                              customer_id
                              INT
                              PRIMARY
                              KEY,
                              customer_name
                              VARCHAR
                          (
                              50
                          ) NOT NULL,
                              total_orders BIGINT NOT NULL
                              )
                          """))

        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS analytics.most_expensive_order_per_customer
                          (
                              customer_id
                              INT
                              PRIMARY
                              KEY,
                              customer_name
                              VARCHAR
                          (
                              50
                          ) NOT NULL,
                              most_expensive_order DECIMAL
                          (
                              18,
                              2
                          ) NOT NULL

                              )
                          """))

        conn.execute(text("""
                          CREATE TABLE IF NOT EXISTS analytics.avg_order_value
                          (
                              customer_id
                              INT
                              PRIMARY
                              KEY,
                              customer_name
                              VARCHAR
                          (
                              50
                          ),
                              total_amount DECIMAL
                          (
                              18,
                              2
                          ) NOT NULL,
                              total_orders BIGINT NOT NULL,
                              avg_order_value DECIMAL
                          (
                              18,
                              2
                          ) NOT NULL
                              )
                          """))
