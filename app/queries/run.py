import logging
import os

from app.main import build_database_url
from sqlalchemy import create_engine
from sqlalchemy import text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO)


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(queries_dir):
        logger.info(f"Loading queries from {file}")
        if file.endswith(".sql"):
            try:
                result = run_query(engine, file)
                logger.info(f"Result for : {file}")
                for row in result:
                    logger.info(row)
            except Exception as e:
                logger.error(f"Error for {file} : {e}")


def run_query(engine, filename: str):
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(queries_dir, filename)) as f:
        query = f.read()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()


if __name__ == '__main__':
    main()
