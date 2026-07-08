import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text

logger = logging.getLogger(__name__)


class TopProductsPipeline(BasePipeline):
    pipeline_name = "top_products"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT p.id                    AS product_id,
                   p.name                  AS product_name,
                   SUM(oi.total_price)     AS total_revenue
            FROM products p
                     JOIN order_items oi ON p.id = oi.product_id
            {where_clause}
            GROUP BY p.id, p.name
        """

    def execute(self):
        query = f"""
            INSERT INTO analytics.top_products (product_id, product_name, total_revenue)
            {self.raw_query(where_clause="WHERE :last_sync IS NULL OR oi.created_at > :last_sync")}
            ON CONFLICT (product_id) DO UPDATE
                SET total_revenue = analytics.top_products.total_revenue + EXCLUDED.total_revenue;
        """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.top_products")

    def update_sync_time(self):
        self._persist_sync_time(self._max_created_at("order_items"))
