import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class TopCustomersPipeline(BasePipeline):
    pipeline_name = "top_customers"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT c.id                AS customer_id,
                   c.name              AS customer_name,
                   CAST(SUM(oi.total_price) AS DECIMAL(18,3)) AS total_amount_spend
            FROM customers c
                     JOIN orders o ON c.id = o.customer_id
                     JOIN order_items oi ON o.id = oi.order_id
            {where_clause}
            GROUP BY c.id, c.name
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.top_customers (customer_id, customer_name, total_amount_spend)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR oi.created_at > :last_sync")}
            ON CONFLICT (customer_id) DO UPDATE
                SET total_amount_spend = analytics.top_customers.total_amount_spend + EXCLUDED.total_amount_spend;
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.top_customers")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("order_items"))

    @property
    def validate_pipeline(self):
        try:
            logger.info(f"Validating top_customers")
            validation_query = f"""
            SELECT EXISTS(
                (
                    SELECT *
                    FROM analytics.top_customers
                    EXCEPT
                    {self.raw_query()}
                )

                UNION ALL

                (
                    {self.raw_query()}
                    EXCEPT
                    SELECT *
                    FROM analytics.top_customers
                )
            )
            """
            has_differences = self.conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
            logger.info(f"validation succeeded for top_customers")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for top_customers: {e}") from e
