import logging

import pandas as pd
from app.database import build_database_url
from app.etl.pipelines.average_order_value_pipeline import AverageOrderValuePipeline
from app.etl.pipelines.customers_with_many_orders_pipeline import CustomersWithManyOrdersPipeline
from app.etl.pipelines.most_expensive_order_per_customer_pipeline import MostExpensiveOrderPerCustomerPipeline
from app.etl.pipelines.orders_per_month_pipeline import OrdersPerMonthPipeline
from app.etl.pipelines.top_customers_pipeline import TopCustomersPipeline
from app.etl.pipelines.top_products_pipeline import TopProductsPipeline
from pandas.testing import assert_frame_equal
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    engine = create_engine(build_database_url())
    with engine.begin() as conn:
        ValidatePipelines.validate_avg_order_value(conn)
        ValidatePipelines.validate_customers_with_many_orders(conn)
        ValidatePipelines.validate_top_products_pipeline(conn)
        ValidatePipelines.validate_orders_per_month_pipeline(conn)
        ValidatePipelines.validate_most_expensive_order_per_customer_pipeline(conn)
        ValidatePipelines.validate_top_customers_pipeline(conn)


class ValidatePipelines:
    def __init__(self):
        pass

    @staticmethod
    # needs changes
    def validate_avg_order_value(conn):
        raw_query = AverageOrderValuePipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)

        materialized_query = """
        SELECT * FROM analytics.avg_order_value;
       """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)
        raw_df = raw_df.sort_values(by="customer_id", ascending=False).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="customer_id", ascending=False).reset_index(drop=True)
        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("avg_order_value validation passed")
        except AssertionError as e:
            logger.error(f"avg_order_value validation failed: {e}")

    @staticmethod
    def validate_customers_with_many_orders(conn):
        raw_query = CustomersWithManyOrdersPipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)

        materialized_query = """
        SELECT * FROM analytics.customers_with_many_orders;
        """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)
        raw_df = raw_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)

        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("customer_with_many_orders validation passed")
        except AssertionError as e:
            logger.error(f"customer_with_many_orders validation failed: {e}")

    @staticmethod
    def validate_most_expensive_order_per_customer_pipeline(conn):
        raw_query = MostExpensiveOrderPerCustomerPipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)

        materialized_query = """
        SELECT * FROM analytics.most_expensive_order_per_customer;
        """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)

        raw_df = raw_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)

        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("most_expensive_order_per_customer_pipeline validation passed")
        except AssertionError as e:
            logger.error(f"most_expensive_order_per_customer_pipeline validation failed: {e}")

    @staticmethod
    def validate_orders_per_month_pipeline(conn):
        raw_query = OrdersPerMonthPipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)
        materialized_query = """
        SELECT * FROM analytics.orders_per_month ;
        """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)
        raw_df = raw_df.sort_values(by="month", ascending=True).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="month", ascending=True).reset_index(drop=True)

        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("orders_per_month_pipeline validation passed")
        except AssertionError as e:
            logger.error(f"orders_per_month_pipeline validation failed: {e}")

    @staticmethod
    def validate_top_customers_pipeline(conn):
        raw_query = TopCustomersPipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)
        materialized_query = """
        SELECT * FROM analytics.top_customers ;
        """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)
        raw_df = raw_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="customer_id", ascending=True).reset_index(drop=True)

        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("top_customers_pipeline validation passed")
        except AssertionError as e:
            logger.error(f"top_customers_pipeline validation failed: {e}")

    @staticmethod
    def validate_top_products_pipeline(conn):
        raw_query = TopProductsPipeline.raw_query()
        raw_df = pd.read_sql_query(text(raw_query), conn)
        materialized_query = """
        SELECT * FROM analytics.top_products ;
        """
        materialized_df = pd.read_sql_query(text(materialized_query), conn)
        raw_df = raw_df.sort_values(by="product_id", ascending=True).reset_index(drop=True)
        materialized_df = materialized_df.sort_values(by="product_id", ascending=True).reset_index(drop=True)

        try:
            assert_frame_equal(raw_df, materialized_df)
            logger.info("top_products_pipeline validation passed")
        except AssertionError as e:
            logger.error(f"top_products_pipeline validation failed: {e}")


if __name__ == "__main__":
    main()
