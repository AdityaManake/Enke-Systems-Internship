import logging

from app.database import build_database_url
from app.etl.analytics_schema import create_analytics_schema
from app.etl.base_pipeline import BasePipeline
from app.etl.metadata import get_last_synced
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    try:
        database_url = build_database_url()
        engine = create_engine(database_url)
        create_analytics_schema(engine)
        with engine.begin() as conn:
            orders_per_month_last_sync = get_last_synced(engine, "orders_per_month")
            top_customers_last_sync = get_last_synced(engine, "top_customers")
            pipelines = [
                OrdersPerMonthPipeline(conn, orders_per_month_last_sync),
                TopProductsPipeline(conn, top_customers_last_sync),
            ]
            for pipeline in pipelines:
                pipeline.run()


    except Exception as e:
        logger.exception(e)
        raise


class OrdersPerMonthPipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "orders_per_month"

    def execute(self):
        query = """
                INSERT INTO analytics.orders_per_month(month, total_orders)

                SELECT DATE_TRUNC('month', ordered_at) ::DATE AS month,
                    COUNT(*) AS total_orders
                FROM orders
                WHERE :last_sync IS NULL
                   OR created_at
                    > :last_sync
                GROUP BY DATE_TRUNC('month', ordered_at)

                ON CONFLICT (month)
                    DO
                UPDATE
                    SET total_orders =
                    analytics.orders_per_month.total_orders
                    + EXCLUDED.total_orders; \
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.orders_per_month")


class TopProductsPipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "top_customers"

    def execute(self):
        query = """
                INSERT into analytics.top_products
                    (product_id, product_name, total_revenue)
                SELECT p.id, p.name, SUM(oi.total_price)
                FROM products p
                         JOIN order_items oi
                              ON p.id = oi.product_id
                WHERE :last_sync IS NULL
                   OR oi.created_at > :last_sync
                GROUP BY p.id, p.name ON CONFLICT (product_id)
                DO
                UPDATE
                    SET total_revenue = analytics.top_products.total_revenue + EXCLUDED.total_revenue; \
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.top_products")


if __name__ == "__main__":
    main()
