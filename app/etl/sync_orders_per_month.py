import logging
from datetime import datetime, UTC
from pathlib import Path

import pandas as pd
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
    create_analytics_schema(engine)
    etl_start_time = datetime.now(UTC)
    last_sync = get_last_synced(engine, "orders_per_month")
    logger.info("Starting incremental sync")
    incremental_orders_per_month(engine, base_dir, last_sync)
    logger.info("Updating analytics.orders_per_month")
    update_last_synced(engine, "orders_per_month", etl_start_time)
    logger.info("Updating metadata")


def incremental_orders_per_month(engine, base_dir, last_sync, ):
    try:
        query_file = base_dir / "queries" / "incremental_orders_per_month.sql"
        with open(query_file, "r") as f:
            query = f.read()

        data = pd.read_sql_query(text(query), engine, params={"last_sync": last_sync})
        delta_df = pd.DataFrame(data)
        with engine.begin() as conn:
            for _, row in delta_df.iterrows():
                conn.execute(text("""
                                  INSERT INTO analytics.orders_per_month(month, total_orders)
                                  VALUES (:month, :total_orders) ON CONFLICT(month)
                                    DO
                                  UPDATE SET total_orders = analytics.orders_per_month.total_orders + EXCLUDED.total_orders

                                  """),
                             {
                                 "month": row["month"],
                                 "total_orders": row["new_orders"]
                             }

                             )
        logger.info(f"Loaded {len(delta_df)} rows in analytics schema")
        return delta_df
    except Exception as e:
        logger.exception(e)
        raise


if __name__ == "__main__":
    main()
