import logging
import time
from pathlib import Path

import pandas as pd
from app.database import build_database_url
from app.etl.analytics_schema import create_analytics_schema
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    create_analytics_schema(engine)
    BASE_DIR = Path(__file__).resolve().parent.parent
    top_customers(engine, BASE_DIR)
    top_products(engine, BASE_DIR)
    average_order_value(engine, BASE_DIR)
    customers_with_many_orders(engine, BASE_DIR)
    most_expensive_order_per_customer(engine, BASE_DIR)
    never_ordered_products(engine, BASE_DIR)
    orders_per_month(engine, BASE_DIR)


def top_customers(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "top_customers.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        customer_df = pd.DataFrame(data)
        logger.info("Extracted top customers")
        customer_df.to_sql("top_customers", engine, schema="analytics", if_exists="replace", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(customer_df)} rows in analytics schema")
        logger.info(f"Top customers completed in: {elapsed:.2f} seconds")
        return customer_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading top customers: {e}")


def top_products(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "top_products.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        product_df = pd.DataFrame(data)
        logger.info("Extracted top products")
        product_df.to_sql("top_products", engine, schema="analytics", if_exists="replace", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(product_df)} in analytics schema")
        logger.info(f"Top products completed in: {elapsed:.2f} seconds")
        return product_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading products: {e}")


def average_order_value(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "avg_order_value.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        average_order_value_df = pd.DataFrame(data)
        logger.info("Extracted average order value")
        average_order_value_df.to_sql("avg_order_value", engine, schema="analytics", if_exists="replace", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(average_order_value_df)} rows analytics schema")
        logger.info(f"Average order value completed in: {elapsed:.2f} seconds")
        return average_order_value_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading average order value: {e}")


def customers_with_many_orders(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "customers_with_many_orders.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        customers_with_many_orders_df = pd.DataFrame(data)
        logger.info("Extracted customers with many orders")
        customers_with_many_orders_df.to_sql("customers_with_many_orders", engine, schema="analytics",
                                             if_exists="replace", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(customers_with_many_orders_df)} rows in analytics schema")
        logger.info(f"Customers with many orders completed in: {elapsed:.2f} seconds")
        return customers_with_many_orders_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading customers with many orders: {e}")


def most_expensive_order_per_customer(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "most_expensive_order_per_customer.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        most_expensive_order_df = pd.DataFrame(data)
        logger.info("Extracted most expensive  order per customer")
        most_expensive_order_df.to_sql("most_expensive_order_per_customer", engine, schema="analytics",
                                       if_exists="replace",
                                       index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(most_expensive_order_df)} rows in analytics schema")
        logger.info(f"Most expensive order per customer completed in: {elapsed:.2f} seconds")
        return most_expensive_order_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading most expensive order per customer: {e}")


def never_ordered_products(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "never_ordered_products.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        never_ordered_product_df = pd.DataFrame(data)
        logger.info("Extracted never ordered products")
        never_ordered_product_df.to_sql("never_ordered_products", engine, schema="analytics", if_exists="replace",
                                        index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(never_ordered_product_df)} rows analytics schema")
        logger.info(f"Never ordered products completed in: {elapsed:.2f} seconds")
        return never_ordered_product_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading never ordered products: {e}")


def orders_per_month(engine, base_dir):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "orders_per_month.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(query, engine)
        orders_per_month_df = pd.DataFrame(data)
        logger.info("Extracted orders per month")
        orders_per_month_df.to_sql("orders_per_month", engine, schema="analytics", if_exists="replace", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(orders_per_month_df)} row in analytics schema")
        logger.info(f"Orders per month completed in: {elapsed:.2f} seconds")
        return orders_per_month_df
    except Exception as e:
        logger.error(f"Got error while extracting & Loading orders per month: {e}")


if __name__ == "__main__":
    main()
