import logging
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
from app.etl.validate_pipelines import ValidatePipelines
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
    def __init__(self, engine, pipeline_classes=None):
        self.engine = engine
        self.metadata = EtlMetadata(engine)
        self.pipeline_classes = pipeline_classes or DEFAULT_PIPELINE_CLASSES

    def run_all(self):
        with self.engine.begin() as conn:
            for pipeline_cls in self.pipeline_classes:
                pipeline = self._build_pipeline(pipeline_cls, conn)
                logger.info(f"Running {pipeline.pipeline_name}")
                start = time.perf_counter()
                pipeline.run()

                elapsed = time.perf_counter() - start
                logger.info(f"Finished {pipeline.pipeline_name} in {elapsed:.4f}s")

            validators = [
                ValidatePipelines.validate_avg_order_value_pipeline,
                ValidatePipelines.validate_customers_with_many_orders_pipeline,
                ValidatePipelines.validate_most_expensive_order_per_customer_pipeline,
                ValidatePipelines.validate_orders_per_month_pipeline,
                ValidatePipelines.validate_top_customers_pipeline,
                ValidatePipelines.validate_top_products_pipeline,
            ]

            logger.info("Running validation checks...")
            for validator in validators:
                validator(conn)
                logger.info(f" {validator.__name__} passed")
            logger.info("All validation checks passed.")

    def _build_pipeline(self, pipeline_cls, conn):
        last_sync = self.metadata.get_last_synced(pipeline_cls.pipeline_name)
        return pipeline_cls(conn, last_sync, self.metadata)


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    create_analytics_schema(engine)
    runner = PipelinesRunner(engine)
    runner.run_all()


if __name__ == "__main__":
    main()
