import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class CustomersWithManyOrdersPipeline(BasePipeline):
    """Materializes total order count per customer.

    raw_query() intentionally has no `HAVING total_orders > 5`: it accumulates
    incrementally, so filtering per-batch would permanently drop customers who
    only cross the threshold in a later sync. The ">5" cut is a read-time
    concern for whoever queries analytics.customers_with_many_orders.
    """

    pipeline_name = "customers_with_many_orders"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT c.id       AS customer_id,
                   c.name     AS customer_name,
                   COUNT(o.id) AS total_orders
            FROM customers c
                     JOIN orders o ON c.id = o.customer_id
            {where_clause}
            GROUP BY c.id, c.name
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.customers_with_many_orders (customer_id, customer_name, total_orders)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR o.created_at > :last_sync")}
            ON CONFLICT (customer_id) DO UPDATE
                SET total_orders = analytics.customers_with_many_orders.total_orders + EXCLUDED.total_orders;
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.customers_with_many_orders")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("orders"))

    @property
    def validate_pipeline(self):
        try:
            logger.info(f"Validating customers_with_many_orders ")
            validation_query = f"""
                        SELECT EXISTS(
                            (
                                SELECT *
                                FROM analytics.customers_with_many_orders
                                EXCEPT
                                {self.raw_query()}
                            )

                            UNION ALL

                            (
                                {self.raw_query()}
                                EXCEPT
                                SELECT *
                                FROM analytics.customers_with_many_orders
                            )
                        )
                        """
            has_differences = self.conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
            logger.info(f"validation succeeded for customers with many orders")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for customers_with_many_orders: {e}") from e
