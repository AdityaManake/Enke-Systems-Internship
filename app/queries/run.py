import logging
import os
import time
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import pandas as pd
from app.database import build_database_url
from app.etl.pipelines.average_order_value_pipeline import AverageOrderValuePipeline
from app.etl.pipelines.customers_with_many_orders_pipeline import CustomersWithManyOrdersPipeline
from app.etl.pipelines.most_expensive_order_per_customer_pipeline import MostExpensiveOrderPerCustomerPipeline
from app.etl.pipelines.orders_per_month_pipeline import OrdersPerMonthPipeline
from app.etl.pipelines.top_customers_pipeline import TopCustomersPipeline
from app.etl.pipelines.top_products_pipeline import TopProductsPipeline
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CHARTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "charts")

NEVER_ORDERED_PRODUCTS_QUERY = """
    SELECT p.id, p.name
    FROM products p
             LEFT JOIN order_items oi ON p.id = oi.product_id
    WHERE oi.product_id IS NULL
"""


class QueryPerformance:
    """Runs a raw SQL string against the engine and times it."""

    def __init__(self, engine):
        self.engine = engine

    def run(self, query: str) -> tuple[pd.DataFrame, float]:
        start = time.perf_counter()
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            df = pd.DataFrame(result.fetchall(), columns=result.keys())
        elapsed = time.perf_counter() - start
        return df, elapsed


class Chart(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def plot(self, df: pd.DataFrame):
        raise NotImplementedError

    def save(self, df: pd.DataFrame, suffix: str):
        os.makedirs(CHARTS_DIR, exist_ok=True)
        plt.figure(figsize=(12, 6))
        self.plot(df)
        plt.tight_layout()
        path = os.path.join(CHARTS_DIR, f"{self.name}_{suffix}.png")
        plt.savefig(path)
        plt.close()
        logger.info(f"Saved chart to {path}")


class BarChart(Chart):
    def __init__(self, name, x, y, xlabel, ylabel, rotate_labels=False):
        super().__init__(name)
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.rotate_labels = rotate_labels

    def plot(self, df):
        x_data = df[self.x].astype(str)
        plt.bar(x_data, df[self.y], color="blue", width=0.6)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        if self.rotate_labels:
            plt.xticks(rotation=45, ha="right")


class LineChart(Chart):
    def __init__(self, name, x, y, xlabel, ylabel):
        super().__init__(name)
        self.x = x
        self.y = y
        self.xlabel = xlabel
        self.ylabel = ylabel

    def plot(self, df):
        x_data = df[self.x].astype(str)
        plt.plot(x_data, df[self.y], color="blue", marker="o")
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)


class ChartQuery:
    """Ties one ETL pipeline's raw_query() to its materialized table and a chart.

    raw_query() (defined once on the pipeline, see app/etl/pipelines) is the
    single source of truth for the aggregation SQL - no separate copy lives
    here. Every run times the raw query against the source tables against the
    materialized analytics table, so raw-vs-materialized performance is always
    visible, and renders the chart from the materialized result.
    """

    def __init__(self, pipeline_cls, materialized_table: str, chart: Chart, transform=None):
        self.pipeline_cls = pipeline_cls
        self.materialized_table = materialized_table
        self.chart = chart
        self.transform = transform or (lambda df: df)

    def run(self, perf: QueryPerformance):
        raw_df, raw_seconds = perf.run(self.pipeline_cls.raw_query())
        materialized_df, materialized_seconds = perf.run(f"SELECT * FROM analytics.{self.materialized_table}")
        speedup = raw_seconds / materialized_seconds if materialized_seconds else float("inf")
        logger.info(
            f"{self.chart.name}: raw={raw_seconds:.4f}s materialized={materialized_seconds:.4f}s "
            f"speedup={speedup:.1f}x"
        )
        self.chart.save(self.transform(raw_df), "raw")
        self.chart.save(self.transform(materialized_df), "materialized")


def build_chart_queries():
    return [
        ChartQuery(
            TopCustomersPipeline, "top_customers",
            BarChart("customer_vs_amount", x="customer_name", y="total_amount_spend",
                     xlabel="Customers", ylabel="Revenue", rotate_labels=True),
            transform=lambda df: df.assign(total_amount_spend=df["total_amount_spend"].astype(float)).nlargest(10, "total_amount_spend"),
        ),
        ChartQuery(
            TopProductsPipeline, "top_products",
            BarChart("product_vs_revenue", x="product_name", y="total_revenue",
                     xlabel="Products", ylabel="Revenue"),
            transform=lambda df: df.assign(total_revenue=df["total_revenue"].astype(float)).nlargest(10, "total_revenue"),
        ),
        ChartQuery(
            OrdersPerMonthPipeline, "orders_per_month",
            LineChart("orders_per_month", x="month", y="total_orders",
                      xlabel="Month", ylabel="Total Orders"),
        ),
        ChartQuery(
            CustomersWithManyOrdersPipeline, "customers_with_many_orders",
            BarChart("customer_vs_ordercount", x="customer_id", y="total_orders",
                     xlabel="Customers", ylabel="Total Orders"),
            # the ">5" cut is a read-time concern, kept out of the pipeline's raw_query()
            # so incremental accumulation stays correct - see CustomersWithManyOrdersPipeline.
            transform=lambda df: df[df["total_orders"].astype(int) > 5].assign(total_orders=lambda d: d["total_orders"].astype(int)).nlargest(10, "total_orders"),
        ),
        ChartQuery(
            MostExpensiveOrderPerCustomerPipeline, "most_expensive_order_per_customer",
            LineChart("mostexpensive_order_per_customer", x="customer_id", y="most_expensive_order",
                      xlabel="Customers", ylabel="Most Expensive Orders"),
            transform=lambda df: df.assign(most_expensive_order=df["most_expensive_order"].astype(float)).nlargest(20, "most_expensive_order"),
        ),
        ChartQuery(
            AverageOrderValuePipeline, "avg_order_value",
            BarChart("ordervalue_vs_customers", x="customer_id", y="avg_order_value",
                     xlabel="Customers", ylabel="Average Order Value"),
            transform=lambda df: df.assign(avg_order_value=df["avg_order_value"].astype(float)).nlargest(10, "avg_order_value"),
        ),
    ]


def log_never_ordered_products(perf: QueryPerformance):
    never_ordered, _ = perf.run(NEVER_ORDERED_PRODUCTS_QUERY)
    logger.info(f"Count of products that were never ordered: {len(never_ordered)}")


def main():
    engine = create_engine(build_database_url())
    perf = QueryPerformance(engine)

    for chart_query in build_chart_queries():
        chart_query.run(perf)

    log_never_ordered_products(perf)


if __name__ == '__main__':
    main()
