import logging

from app.etl.base_pipeline import BasePipeline
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class TopProductsPipeline(BasePipeline):
    pipeline_name = "top_products"

    @staticmethod
    def raw_query(where_clause: str = "") -> str:
        return f"""
            SELECT p.id                    AS product_id,
                   p.name                  AS product_name,
                   CAST(SUM(oi.total_price) AS DECIMAL(18,3)) AS total_revenue
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

    @property
    def validate_pipeline(self):
        try:
            logger.info(f"Validating top_products")
            validation_query = f"""
            SELECT EXISTS(
                (
                    SELECT *
                    FROM analytics.top_products
                    EXCEPT
                    {self.raw_query()}
                )

                UNION ALL

                (
                    {self.raw_query()}
                    EXCEPT
                    SELECT *
                    FROM analytics.top_products
                )
            )
            """
            has_differences = self.conn.execute(text(validation_query)).scalar_one()
            if has_differences:
                raise ValueError("Validation failed: the materialized data does not match the source data.")
            logger.info(f"validation succeeded for top_products")
        except (SQLAlchemyError, ValueError) as e:
            raise Exception(f"Validation failed for top_products: {e}") from e
