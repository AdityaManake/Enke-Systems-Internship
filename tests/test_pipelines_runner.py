import pytest
from app.etl.pipelines.top_products_pipeline import TopProductsPipeline
from app.etl.pipelines_runner import PipelinesRunner
from sqlalchemy import text


def test_happy_path(engine, seed_source_data):
    runner = PipelinesRunner(engine, seed_source_data)
    runner.run_all()

    tables = [
        "analytics.orders_per_month", "analytics.customers_with_many_orders",
        "analytics.most_expensive_order_per_customer",
        "analytics.orders_per_month", "analytics.top_customers", "analytics.top_products"
    ]

    with engine.connect() as conn:
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            assert count > 0, f"Table {table} is empty"

        metadata_count = conn.execute(text(f"SELECT COUNT(*) FROM analytics.etl_metadata")).scalar()
        assert metadata_count == 6


def test_transaction_rollback(engine, seed_source_data, monkeypatch):
    @property
    def mock_failing_validation(self):
        raise ValueError("Simulated validation failure")

    monkeypatch.setattr(TopProductsPipeline, "validate_pipeline", mock_failing_validation)
    runner = PipelinesRunner(engine)

    with pytest.raises(ValueError, match="Simulated validation failure"):
        runner.run_all()

    tables = [
        "analytics.orders_per_month",
        "analytics.top_products",
        "analytics.top_customers",
        "analytics.customers_with_many_orders",
        "analytics.most_expensive_order_per_customer",
        "analytics.avg_order_value",
        "analytics.etl_metadata",
    ]

    with engine.connect() as conn:
        for table in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            assert count == 0, f"Table {table} has data, rollback failed!"


def test_repeated_incremental_execution(engine, seed_source_data):
    runner = PipelinesRunner(engine)
    runner.run_all()
    with engine.connect() as conn:
        initial_revenue = conn.execute(
            text("SELECT total_revenue FROM analytics.top_products WHERE product_id = 1")
        ).scalar()
        assert float(initial_revenue) == 30.00
        last_sync_before = conn.execute(
            text("SELECT last_sync_time FROM analytics.etl_metadata WHERE table_name = 'top_products'")
        ).scalar()
        assert last_sync_before is not None
    with engine.begin() as conn:
        conn.execute(text("""
                INSERT INTO orders (id, customer_id, ordered_at, created_at) VALUES 
                (3, 1, '2026-07-03 10:00:00', '2026-07-03 10:00:00')
            """))
        conn.execute(text("""
                INSERT INTO order_items (order_id, product_id, quantity, total_price, created_at) VALUES
                (3, 1, 3, 30.00, '2026-07-03 10:00:00')
            """))
    runner.run_all()
    with engine.connect() as conn:
        updated_revenue = conn.execute(
            text("SELECT total_revenue FROM analytics.top_products WHERE product_id = 1")
        ).scalar()
        assert float(updated_revenue) == 60.00
        total_products_rows = conn.execute(text("SELECT COUNT(*) FROM analytics.top_products")).scalar()
        assert total_products_rows == 1
        last_sync_after = conn.execute(
            text("SELECT last_sync_time FROM analytics.etl_metadata WHERE table_name = 'top_products'")
        ).scalar()
        assert last_sync_after > last_sync_before
