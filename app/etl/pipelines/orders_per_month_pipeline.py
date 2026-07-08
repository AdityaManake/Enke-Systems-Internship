import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text

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
