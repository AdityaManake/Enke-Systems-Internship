import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class AverageOrderValuePipeline(BasePipeline):
    pipeline_name = "avg_order_value"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT c.id                              AS customer_id,
                   c.name                             AS customer_name,
                   CAST(SUM(order_totals.order_total) AS DECIMAL(18,2)) AS total_amount,
                   COUNT(o.id)                        AS total_orders,
                   CAST(AVG(order_totals.order_total) AS DECIMAL(18,2)) AS avg_order_value
            FROM customers c
                     JOIN orders o ON c.id = o.customer_id
                     JOIN (SELECT order_id, SUM(total_price) AS order_total
                           FROM order_items
                           GROUP BY order_id) order_totals
                          ON o.id = order_totals.order_id
            {where_clause}
            GROUP BY c.id, c.name
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.avg_order_value
                (customer_id, customer_name, total_amount, total_orders, avg_order_value)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR o.created_at > :last_sync")}
            ON CONFLICT (customer_id) DO UPDATE
                SET total_amount = analytics.avg_order_value.total_amount + EXCLUDED.total_amount,
                    total_orders = analytics.avg_order_value.total_orders + EXCLUDED.total_orders,
                    avg_order_value = (
                        analytics.avg_order_value.total_amount + EXCLUDED.total_amount
                    ) / (
                        analytics.avg_order_value.total_orders + EXCLUDED.total_orders
                    );
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.avg_order_value")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("orders"))

    @property
    def validate_pipeline(self):
        try:
            logger.info(f"Validating top_products")
            validation_query = f"""
            SELECT EXISTS(
                (
                    SELECT *
                    FROM analytics.avg_order_value
                    EXCEPT
                    {self.raw_query()}
                )

                UNION ALL

                (
                    {self.raw_query()}
                    EXCEPT
                    SELECT *
                    FROM analytics.avg_order_value
                )
            )
            """
            has_differences = self.conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
            logger.info(f"validation succeeded for top_products")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for top_products: {e}") from e
