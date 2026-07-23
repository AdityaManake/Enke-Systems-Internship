import pytest
from app.database import Base
from app.etl.analytics_schema import create_analytics_schema
from app.models.customer import Customer  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_items import OrderItem  # noqa: F401
from app.models.product import Product  # noqa: F401
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer


@pytest.fixture(scope="session")
def engine():
    with PostgresContainer("postgres:16") as pg:
        engine = create_engine(pg.get_connection_url())
        Base.metadata.create_all(engine)  # customers/products/orders/order_items
        create_analytics_schema(engine)  # analytics.*
        yield engine
        engine.dispose()


@pytest.fixture(autouse=True)
def clean_tables(engine):
    yield
    tables = [
        "order_items", "orders", "products", "customers",
        "analytics.etl_metadata", "analytics.orders_per_month",
        "analytics.top_products", "analytics.top_customers",
        "analytics.customers_with_many_orders",
        "analytics.most_expensive_order_per_customer",
        "analytics.avg_order_value",
    ]
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"))


@pytest.fixture
def seed_source_data(engine):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO customers (id, email, name) VALUES
            (1, 'a@test.com', 'Alice'), (2, 'b@test.com', 'Bob')
        """))
        conn.execute(text("""
            INSERT INTO products (id, name, price) VALUES
            (1, 'Widget', 10.00)
        """))
        conn.execute(text("""
            INSERT INTO orders (id, customer_id, ordered_at, created_at) VALUES 
            (1, 1, '2026-07-01 10:00:00', '2026-07-01 10:00:00'), (2, 2, '2026-07-02 10:00:00', '2026-07-02 10:00:00')
        """))
        conn.execute(text("""
            INSERT INTO order_items (order_id, product_id, quantity, total_price, created_at) VALUES
            (1, 1, 2, 20.00, '2026-07-01 10:00:00'), (2, 1, 1, 10.00, '2026-07-02 10:00:00')
        """))
