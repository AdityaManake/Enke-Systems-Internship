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
            top_products_last_sync = get_last_synced(engine, "top_products")
            top_customers_last_sync = get_last_synced(engine, "top_customers")
            customers_with_many_orders_last_sync = get_last_synced(engine, "customers_with_many_orders")
            most_expensive_orders_last_sync = get_last_synced(engine, "most_expensive_order_per_customer")
            average_order_value_last_sync = get_last_synced(engine, "avg_order_value")
            pipelines = [
                OrdersPerMonthPipeline(conn, orders_per_month_last_sync),
                TopProductsPipeline(conn, top_products_last_sync),
                TopCustomersPipeline(conn, top_customers_last_sync),
                CustomersWithManyOrdersPipeline(conn, customers_with_many_orders_last_sync),
                MostExpensiveOrderPerCustomerPipeline(conn, most_expensive_orders_last_sync),
                AverageOrderValuePipeline(conn, average_order_value_last_sync),
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

    @property
    def source_table(self):
        return "orders"

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
        return "top_products"

    @property
    def source_table(self):
        return "order_items"

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


class TopCustomersPipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "top_customers"

    @property
    def source_table(self):
        return "order_items"

    def execute(self):
        query = """
                INSERT INTO analytics.top_customers (customer_id, customer_name, total_amount_spend)
                SELECT c.id, c.name, SUM(oi.total_price)
                FROM customers c
                         JOIN orders o ON c.id = o.customer_id
                         JOIN order_items oi ON o.id = oi.order_id
                WHERE :last_sync IS NULL
                   OR oi.created_at > :last_sync
                GROUP BY c.id, c.name ON CONFLICT (customer_id) DO
                UPDATE
                    SET total_amount_spend = analytics.top_customers.total_amount_spend + EXCLUDED.total_amount_spend; \
 \
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.top_customers")


class CustomersWithManyOrdersPipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "customers_with_many_orders"

    @property
    def source_table(self):
        return "orders"

    def execute(self):
        query = """
                INSERT INTO analytics.customers_with_many_orders
                (customer_id,
                 customer_name,
                 total_orders)

                SELECT c.id,
                       c.name,
                       COUNT(o.id)
                FROM customers c
                         JOIN orders o
                              ON c.id = o.customer_id
                WHERE :last_sync IS NULL
                   OR o.created_at > :last_sync
                GROUP BY c.id, c.name ON CONFLICT (customer_id)
                DO
                UPDATE
                    SET total_orders =
                    analytics.customers_with_many_orders.total_orders
                    + EXCLUDED.total_orders;
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.customers_with_many_orders")


class MostExpensiveOrderPerCustomerPipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "most_expensive_order_per_customer"

    @property
    def source_table(self):
        return "orders"

    def execute(self):
        query = """
                INSERT INTO analytics.most_expensive_order_per_customer (customer_id, customer_name, most_expensive_order)
                SELECT c.id, c.name, MAX(order_totals.order_total)
                FROM customers c
                         JOIN orders o ON c.id = o.customer_id
                         JOIN (SELECT order_id, SUM(total_price) AS order_total
                               FROM order_items
                               GROUP BY order_id) AS order_totals
                              ON o.id = order_totals.order_id
                WHERE :last_sync IS NULL
                   OR o.created_at > :last_sync
                GROUP BY c.id, c.name ON CONFLICT (customer_id) DO
                UPDATE
                    SET most_expensive_order =
                    GREATEST(
                    analytics.most_expensive_order_per_customer.most_expensive_order,
                    EXCLUDED.most_expensive_order
                    );
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.most_expensive_order_per_customer")


class AverageOrderValuePipeline(BasePipeline):
    @property
    def pipeline_name(self):
        return "avg_order_value"

    @property
    def source_table(self):
        return "orders"

    def execute(self):
        query = """
                INSERT INTO analytics.avg_order_value
                (customer_id,
                 customer_name,
                 total_amount,
                 total_orders,
                 avg_order_value)

                SELECT c.id,
                       c.name,
                       SUM(order_totals.order_total),
                       COUNT(o.id),
                       AVG(order_totals.order_total)
                FROM customers c
                         JOIN orders o
                              ON c.id = o.customer_id
                         JOIN (SELECT order_id,
                                      SUM(total_price) AS order_total
                               FROM order_items
                               GROUP BY order_id) order_totals
                              ON o.id = order_totals.order_id
                WHERE :last_sync IS NULL
                   OR o.created_at > :last_sync
                GROUP BY c.id, c.name ON CONFLICT (customer_id)
DO
                UPDATE
                    SET
                        total_amount =
                    analytics.avg_order_value.total_amount
                    + EXCLUDED.total_amount,

                    total_orders =
                    analytics.avg_order_value.total_orders
                    + EXCLUDED.total_orders,

                    avg_order_value =
                    (
                    analytics.avg_order_value.total_amount
                    + EXCLUDED.total_amount
                    )
                    /
                    (
                    analytics.avg_order_value.total_orders
                    + EXCLUDED.total_orders
                    );
                """
        self.conn.execute(text(query), {"last_sync": self.last_sync})
        logger.info("Updated analytics.average_order_value")


if __name__ == "__main__":
    main()
