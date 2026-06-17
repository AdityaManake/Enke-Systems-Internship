from app.database import build_database_url
from sqlalchemy import create_engine


def main():
    engine = create_engine(build_database_url())
    create_analytics_schema(engine)


def create_analytics_schema(engine):
    with engine.connect() as conn:
        conn.execute(
            "CREATE SCHEMA analytics;"
        )
