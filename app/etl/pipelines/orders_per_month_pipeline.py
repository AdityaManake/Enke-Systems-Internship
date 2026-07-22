import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class OrdersPerMonthPipeline(BasePipeline):
    pipeline_name = "orders_per_month"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT DATE_TRUNC('month', ordered_at)::DATE AS month,
                   COUNT(*)                              AS total_orders
            FROM orders
            {where_clause}
            GROUP BY DATE_TRUNC('month', ordered_at)
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.orders_per_month(month, total_orders)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR created_at > :last_sync")}
            ON CONFLICT (month) DO UPDATE
                SET total_orders = analytics.orders_per_month.total_orders + EXCLUDED.total_orders;
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.orders_per_month")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("orders"))

    @property
    def validate_pipeline(self):
        try:
            logger.info(f"Validating orders_per_month")
            validation_query = f"""
            SELECT EXISTS(
                (
                    SELECT *
                    FROM analytics.orders_per_month
                    EXCEPT
                    {self.raw_query()}
                )

                UNION ALL

                (
                    {self.raw_query()}
                    EXCEPT
                    SELECT *
                    FROM analytics.orders_per_month
                )
            )
            """
            has_differences = self.conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
            logger.info(f"validation succeeded for orders_per_month")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for orders_per_month: {e}") from e
