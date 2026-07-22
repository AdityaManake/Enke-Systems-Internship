import argparse
import logging
import sys
import time

from app.database import build_database_url
from app.etl.analytics_schema import create_analytics_schema
from app.etl.etl_metadata import EtlMetadata
from app.etl.pipelines.average_order_value_pipeline import AverageOrderValuePipeline
from app.etl.pipelines.customers_with_many_orders_pipeline import CustomersWithManyOrdersPipeline
from app.etl.pipelines.most_expensive_order_per_customer_pipeline import MostExpensiveOrderPerCustomerPipeline
from app.etl.pipelines.orders_per_month_pipeline import OrdersPerMonthPipeline
from app.etl.pipelines.top_customers_pipeline import TopCustomersPipeline
from app.etl.pipelines.top_products_pipeline import TopProductsPipeline
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

DEFAULT_PIPELINE_CLASSES = [
    OrdersPerMonthPipeline,
    TopProductsPipeline,
    TopCustomersPipeline,
    CustomersWithManyOrdersPipeline,
    MostExpensiveOrderPerCustomerPipeline,
    AverageOrderValuePipeline,
]


class PipelinesRunner:
    def __init__(self, engine, pipeline_classes=None, pipeline_names=None):
        self.engine = engine
        self.metadata = EtlMetadata(engine)
        initial_classes = pipeline_classes or DEFAULT_PIPELINE_CLASSES
        if pipeline_names:
            valid_names = {cls.pipeline_name for cls in initial_classes}
            invalid_names = set(pipeline_names) - valid_names
            if invalid_names:
                raise ValueError(
                    f"Invalid pipeline name(s): {', '.join(invalid_names)}. "
                    f"Valid options are: {', '.join(sorted(valid_names))}"
                )
            self.pipeline_classes = [cls for cls in initial_classes if cls.pipeline_name in pipeline_names]
        else:
            self.pipeline_classes = initial_classes

    def run_all(self):
        with self.engine.begin() as conn:
            for pipeline_cls in self.pipeline_classes:
                pipeline = self._build_pipeline(pipeline_cls, conn)
                logger.info(f"Running {pipeline.pipeline_name}")
                start = time.perf_counter()
                pipeline.run()

                elapsed = time.perf_counter() - start
                logger.info(f"Finished {pipeline.pipeline_name} in {elapsed:.4f}s")

    def _build_pipeline(self, pipeline_cls, conn):
        last_sync = self.metadata.get_last_synced(pipeline_cls.pipeline_name)
        return pipeline_cls(conn, last_sync, self.metadata)


def main():
    parser = argparse.ArgumentParser(description="Run specific ETL pipelines.")
    parser.add_argument(
        "pipeline_names",
        nargs="*",
        help="Optional names of specific pipelines to run. If none are provided, all pipelines run."
    )
    args = parser.parse_args()
    database_url = build_database_url()
    engine = create_engine(database_url)
    create_analytics_schema(engine)

    try:
        runner = PipelinesRunner(engine, pipeline_names=args.pipeline_names if args.pipeline_names else None)
        runner.run_all()
    except ValueError as e:
        logger.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
