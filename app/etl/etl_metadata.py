from app.database import build_database_url
from sqlalchemy import create_engine, text


class EtlMetadata:
    def __init__(self, engine):
        self.engine = engine

    def get_last_synced(self, table_name):
        query = text(
            """
            SELECT last_sync_time
            FROM analytics.etl_metadata
            WHERE table_name = :table_name
            """
        )
        with self.engine.connect() as conn:
            result = conn.execute(query, {"table_name": table_name}).fetchone()

        return result[0] if result else None

    def update_last_synced(self, conn, table_name, sync_time):
        query = text("""
                     INSERT INTO analytics.etl_metadata(table_name, last_sync_time)
                     VALUES (:table_name, :sync_time) ON CONFLICT (table_name)
                     DO
                     UPDATE SET last_sync_time = EXCLUDED.last_sync_time
                     """)
        conn.execute(query, {"table_name": table_name, "sync_time": sync_time})


def main():
    engine = create_engine(build_database_url())
    EtlMetadata(engine).get_last_synced(table_name="etl_metadata")


if __name__ == "__main__":
    main()
