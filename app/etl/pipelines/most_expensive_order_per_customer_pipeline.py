import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text

logger = logging.getLogger(__name__)


class MostExpensiveOrderPerCustomerPipeline(BasePipeline):
    pipeline_name = "most_expensive_order_per_customer"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT c.id                                  AS customer_id,
                   c.name                                AS customer_name,
                   MAX(order_totals.order_total)          AS most_expensive_order
            FROM customers c
                     JOIN orders o ON c.id = o.customer_id
                     JOIN (SELECT order_id, SUM(total_price) AS order_total
                           FROM order_items
                           GROUP BY order_id) AS order_totals
                          ON o.id = order_totals.order_id
            {where_clause}
            GROUP BY c.id, c.name
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.most_expensive_order_per_customer (customer_id, customer_name, most_expensive_order)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR o.created_at > :last_sync")}
            ON CONFLICT (customer_id) DO UPDATE
                SET most_expensive_order = GREATEST(
                    analytics.most_expensive_order_per_customer.most_expensive_order,
                    EXCLUDED.most_expensive_order
                );
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.most_expensive_order_per_customer")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("orders"))
