import logging

from app.database import build_database_url
from app.etl.pipelines.average_order_value_pipeline import AverageOrderValuePipeline
from app.etl.pipelines.customers_with_many_orders_pipeline import CustomersWithManyOrdersPipeline
from app.etl.pipelines.most_expensive_order_per_customer_pipeline import MostExpensiveOrderPerCustomerPipeline
from app.etl.pipelines.orders_per_month_pipeline import OrdersPerMonthPipeline
from app.etl.pipelines.top_customers_pipeline import TopCustomersPipeline
from app.etl.pipelines.top_products_pipeline import TopProductsPipeline
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

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
    def validate_avg_order_value_pipeline(conn):
        try:
            validation_query = f"""
            SELECT EXISTS(
                (
                    SELECT *
                    FROM analytics.avg_order_value
                    EXCEPT
                    {AverageOrderValuePipeline.raw_query()}
                )

                UNION ALL

                (
                    {AverageOrderValuePipeline.raw_query()}
                    EXCEPT
                    SELECT *
                    FROM analytics.avg_order_value
                )
            )
            """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for avg_order_value: {e}") from e

    @staticmethod
    def validate_customers_with_many_orders_pipeline(conn):
        try:
            validation_query = f"""
                        SELECT EXISTS(
                            (
                                SELECT *
                                FROM analytics.customers_with_many_orders
                                EXCEPT
                                {CustomersWithManyOrdersPipeline.raw_query()}
                            )
    
                            UNION ALL
    
                            (
                                {CustomersWithManyOrdersPipeline.raw_query()}
                                EXCEPT
                                SELECT *
                                FROM analytics.customers_with_many_orders
                            )
                        )
                        """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for customers_with_many_orders: {e}") from e

    @staticmethod
    def validate_most_expensive_order_per_customer_pipeline(conn):
        try:
            validation_query = f"""
                               SELECT EXISTS(
                                   (
                                       SELECT *
                                       FROM analytics.most_expensive_order_per_customer
                                       EXCEPT
                                       {MostExpensiveOrderPerCustomerPipeline.raw_query()}
                                   )

                                   UNION ALL

                                   (
                                       {MostExpensiveOrderPerCustomerPipeline.raw_query()}
                                       EXCEPT
                                       SELECT *
                                       FROM analytics.most_expensive_order_per_customer
                                   )
                               )
                               """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for most_expensive_order_per_customer: {e}") from e

    @staticmethod
    def validate_orders_per_month_pipeline(conn):
        try:
            validation_query = f"""
                                      SELECT EXISTS(
                                          (
                                              SELECT *
                                              FROM analytics.orders_per_month
                                              EXCEPT
                                              {OrdersPerMonthPipeline.raw_query()}
                                          )

                                          UNION ALL

                                          (
                                              {OrdersPerMonthPipeline.raw_query()}
                                              EXCEPT
                                              SELECT *
                                              FROM analytics.orders_per_month
                                          )
                                      )
                                      """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for orders_per_month: {e}") from e

    @staticmethod
    def validate_top_customers_pipeline(conn):
        try:
            validation_query = f"""
                                      SELECT EXISTS(
                                          (
                                              SELECT *
                                              FROM analytics.top_customers
                                              EXCEPT
                                              {TopCustomersPipeline.raw_query()}
                                          )

                                          UNION ALL

                                          (
                                              {TopCustomersPipeline.raw_query()}
                                              EXCEPT
                                              SELECT *
                                              FROM analytics.top_customers
                                          )
                                      )
                                      """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for top_customers: {e}") from e

    @staticmethod
    def validate_top_products_pipeline(conn):
        try:
            validation_query = f"""
                                      SELECT EXISTS(
                                          (
                                              SELECT *
                                              FROM analytics.top_products
                                              EXCEPT
                                              {TopProductsPipeline.raw_query()}
                                          )

                                          UNION ALL

                                          (
                                              {TopProductsPipeline.raw_query()}
                                              EXCEPT
                                              SELECT *
                                              FROM analytics.top_products
                                          )
                                      )
                                      """
            has_differences = conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for top_products: {e}") from e


if __name__ == "__main__":
    main()
