from app.database import build_database_url
from sqlalchemy import create_engine, text


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    get_last_synced(engine, table_name="etl_metadata")


def get_last_synced(engine, table_name):
    query = text(
        """
        SELECT last_sync_time
        FROM analytics.etl_metadata
        WHERE table_name = :table_name
        """
    )
    with engine.connect() as conn:
        result = conn.execute(query, {"table_name": table_name}).fetchone()

    return result[0] if result else None


def update_last_synced(engine, table_name, sync_time):
    query = text("""
                 INSERT INTO analytics.etl_metadata(table_name, last_sync_time)
                 VALUES (:table_name, :sync_time) ON CONFLICT (table_name)
                 DO
                 UPDATE SET last_sync_time =EXCLUDED.last_sync_time
                 """)
    with engine.begin() as conn:
        conn.execute(query, {"table_name": table_name,
                             "sync_time": sync_time})
