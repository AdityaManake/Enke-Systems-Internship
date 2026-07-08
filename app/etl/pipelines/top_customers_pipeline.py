import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text

logger = logging.getLogger(__name__)


class TopCustomersPipeline(BasePipeline):
    pipeline_name = "top_customers"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT c.id                AS customer_id,
                   c.name              AS customer_name,
                   SUM(oi.total_price) AS total_amount_spend
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
