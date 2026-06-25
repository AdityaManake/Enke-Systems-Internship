import logging
from datetime import datetime, UTC
from pathlib import Path

from app.database import build_database_url
from app.etl.analytics_schema import create_analytics_schema
from app.etl.metadata import get_last_synced, update_last_synced
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    engine = create_engine(build_database_url())
    base_dir = Path(__file__).resolve().parent.parent
    logger.info("Starting incremental sync")
    create_analytics_schema(engine)
    etl_start_time = datetime.now(UTC)
    last_sync = get_last_synced(engine, "orders_per_month")
    with engine.begin() as conn:
        incremental_orders_per_month(base_dir, last_sync, conn)
        update_last_synced(conn, "orders_per_month", etl_start_time)
    logger.info("Incremental sync completed")


def incremental_orders_per_month(base_dir, last_sync, conn):
    try:
        query_file = base_dir / "queries" / "incremental_orders_per_month.sql"
        with open(query_file, "r") as f:
            query = f.read()
            conn.execute(text(query), {"last_sync": last_sync})
        logger.info("Updated analytics.orders_per_month")
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == "__main__":
    main()
