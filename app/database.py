import os

from sqlalchemy.orm import declarative_base

Base = declarative_base()


def build_database_url() -> str:
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    return f"postgresql+psycopg2://"f"{db_user}:{db_password}@"f"{db_host}:{db_port}/{db_name}"


if __name__ == "__main__":
    database_url = build_database_url()
