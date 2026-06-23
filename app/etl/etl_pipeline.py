import logging
import time
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
from app.database import build_database_url
from app.etl.analytics_schema import create_analytics_schema
from app.etl.metadata import get_last_synced, update_last_synced
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    try:
        etl_start_time = datetime.now(UTC)

        database_url = build_database_url()
        engine = create_engine(database_url)
        create_analytics_schema(engine)
        customers_last_sync = get_last_synced(engine, "customers")
        logger.info(f"Customers last sync: {customers_last_sync}")
        products_last_sync = get_last_synced(engine, "products")
        logger.info(f"Products last sync: {products_last_sync}")
        orders_last_sync = get_last_synced(engine, "orders")
        logger.info(f"Orders last sync: {orders_last_sync}")
        order_items_last_sync = get_last_synced(engine, "order_items")
        logger.info(f"Order items last sync: {order_items_last_sync}")
        BASE_DIR = Path(__file__).resolve().parent.parent
        new_customers = extract_customers(engine, customers_last_sync)
        new_products = extract_products(engine, products_last_sync)
        new_orders = extract_orders(engine, orders_last_sync)
        new_order_items = extract_order_items(engine, order_items_last_sync)

        logger.info(f"New customers: {len(new_customers)}")
        logger.info(f"New products: {len(new_products)}")
        logger.info(f"New orders: {len(new_orders)}")
        logger.info(f"New order items: {len(new_order_items)}")

        top_customers(engine, BASE_DIR, customers_last_sync)
        top_products(engine, BASE_DIR)
        average_order_value(engine, BASE_DIR)
        customers_with_many_orders(engine, BASE_DIR)
        most_expensive_order_per_customer(engine, BASE_DIR)
        never_ordered_products(engine, BASE_DIR)
        orders_per_month(engine, BASE_DIR)

        update_last_synced(engine, "customers", etl_start_time)
        update_last_synced(engine, "products", etl_start_time)
        update_last_synced(engine, "orders", etl_start_time)
        update_last_synced(engine, "order_items", etl_start_time)
    except Exception as e:
        logger.exception("etl failed")
        raise


def extract_customers(engine, customers_last_sync):
    try:
        if customers_last_sync is None:
            query = """
                    SELECT *
                    FROM customers;
                    """
            return pd.read_sql(query, engine)

        query = """
                SELECT *
                FROM customers
                WHERE created_at > %(last_sync)s
                   OR updated_at > %(last_sync)s \
                """

        return pd.read_sql(query, engine, params={"last_sync": customers_last_sync})

    except Exception as e:
        logger.exception(f"Error while extracting customers : {e} ")
        raise


def extract_products(engine, products_last_sync):
    try:
        if products_last_sync is None:
            query = """
                    SELECT *
                    FROM products; \
                    """

            return pd.read_sql(query, engine)

        query = """
                SELECT *
                FROM products
                WHERE created_at > %(last_sync)s
                   OR updated_at > %(last_sync)s \
                """

        return pd.read_sql(query, engine, params={"last_sync": products_last_sync})
    except Exception as e:
        logger.exception(f"Error while extracting products : {e} ")
        raise


def extract_orders(engine, orders_last_sync):
    try:
        if orders_last_sync is None:
            query = """
                    SELECT *
                    FROM orders;
                    """
            return pd.read_sql(query, engine)

        query = """
                SELECT *
                FROM orders
                WHERE created_at > %(last_sync)s
                   OR updated_at > %(last_sync)s
                """

        return pd.read_sql(query, engine, params={"last_sync": orders_last_sync})
    except Exception as e:
        logger.exception(f"Error while extracting orders : {e} ")
        raise


def extract_order_items(engine, order_items_last_sync):
    try:
        if order_items_last_sync is None:
            query = """
                    SELECT *
                    FROM order_items; \
                    """
            return pd.read_sql(query, engine)

        query = """
                SELECT *
                FROM order_items
                WHERE created_at > %(last_sync)s
                   OR updated_at > %(last_sync)s
                """

        return pd.read_sql(query, engine, params={"last_sync": order_items_last_sync})
    except Exception as e:
        logger.exception(f"Error while extracting order items : {e} ")
        raise


def top_customers(engine, base_dir, customers_last_sync):
    try:
        start = time.time()
        query_file = base_dir / "queries" / "top_customers.sql"
        with open(query_file, "r") as f:
            query = f.read()
        data = pd.read_sql(text(query), engine, params={"last_sync": customers_last_sync})
        customer_df = pd.DataFrame(data)
        logger.info("Extracted top customers")
        customer_df.to_sql("top_customers", engine, schema="analytics", if_exists="append", index=False)
        elapsed = time.time() - start
        logger.info(f"Loaded {len(customer_df)} rows in analytics schema")
        logger.info(f"Top customers completed in: {elapsed:.2f} seconds")
        return customer_df
    except Exception as e:
        logger.exception(f"Got error while extracting & Loading top customers: {e}")
        raise


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
