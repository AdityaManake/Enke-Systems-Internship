import logging
import os

import matplotlib.pyplot as plt
import pandas as pd
from app.database import build_database_url
from sqlalchemy import create_engine
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def main():
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    dict_df = creating_df(queries_dir)
    customer_vs_amount(dict_df, queries_dir)
    product_vs_revenue(dict_df, queries_dir)
    orders_per_month(dict_df, queries_dir)
    ordervalue_vs_customers(dict_df, queries_dir)
    customer_vs_ordercount(dict_df, queries_dir)
    mostexpensive_orders(dict_df, queries_dir)
    products_never_ordered(dict_df)


def creating_df(queries_dir):
    database_url = build_database_url()
    engine = create_engine(database_url)

    df_dict = {}
    for file in os.listdir(queries_dir):
        logger.info(f"Loading queries from {file}")

        if not file.endswith(".sql"):
            continue
        try:
            df_name = file.replace(".sql", "_df")
            df_dict[df_name] = run_query(engine, file)

        except Exception as e:
            logger.error(f"{file}, error: {e}")

    return df_dict


def run_query(engine, filename: str):
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(queries_dir, filename)) as f:
        query = f.read()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
    return df


def customer_vs_amount(df_dict, queries_dir):
    top_customers = df_dict["top_customers_df"]
    logger.info(top_customers.columns.tolist())
    plt.figure(figsize=(12, 6))
    plt.bar(top_customers.name, top_customers.total_amount_spend, color="blue", width=0.6)
    plt.xlabel("Customers")
    plt.ylabel("Revenue")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "customer_vs_amount.png"))
    plt.close()
    logger.info(f"Saving chart for customer_vs_amount")


def product_vs_revenue(df_dict, queries_dir):
    top_products = df_dict["top_products_df"]
    labels = top_products["name"]
    plt.bar(labels, top_products.total_revenue, color="blue", width=0.6)
    plt.xlabel("Products")
    plt.ylabel("Revenue")
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "product_vs_revenue.png"))
    plt.close()
    logger.info(f"Saving chart for product_vs_revenue")


def orders_per_month(df_dict, queries_dir):
    order_per_month = df_dict["orders_per_month_df"]
    plt.plot(order_per_month.month, order_per_month.total_orders, color="blue")
    plt.xlabel("Month")
    plt.ylabel("Total Orders")
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "orders_per_month.png"))
    plt.close()
    logger.info(f"Saving chart for orders_per_month")


def ordervalue_vs_customers(df_dict, queries_dir):
    avg_order_value = df_dict["avg_order_value_df"]
    plt.bar(avg_order_value.id, avg_order_value.average_order_value, color="blue")
    plt.xlabel("Customers")
    plt.ylabel("Average Order Value")
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "ordervalue_vs_customers.png"))
    plt.close()
    logger.info(f"Saving chart for ordervalue_vs_customers")


def customer_vs_ordercount(df_dict, queries_dir):
    customers_with_many_orders = df_dict["customers_with_many_orders_df"]
    plt.bar(customers_with_many_orders.id, customers_with_many_orders.total_orders, color="blue", width=0.6)
    plt.xlabel("Customers")
    plt.ylabel("Total Orders")
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "customer_vs_ordercount.png"))
    plt.close()
    logger.info(f"Saving chart for customer_vs_ordercount")


def mostexpensive_orders(df_dict, queries_dir):
    most_expensive_order_per_customer = df_dict["most_expensive_order_per_customer_df"]
    plt.plot(most_expensive_order_per_customer.id, most_expensive_order_per_customer.most_expensive_order, color="blue")
    plt.xlabel("Customers")
    plt.ylabel("Most Expensive Orders")
    chart_dir = os.path.join(queries_dir, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    plt.savefig(os.path.join(chart_dir, "mostexpensive_order_per_customer.png"))
    plt.close()
    logger.info(f"Saving chart for mostexpensive_order_per_customer")


def products_never_ordered(df_dict):
    logger.info("Count of Products that were never ordered.")
    never_ordered_products = df_dict["never_ordered_products_df"]
    if len(never_ordered_products) > 0:
        len_never_ordered_products = len(never_ordered_products)
    else:
        len_never_ordered_products = 0
    logger.info(f"Count of Products that were never ordered. {len_never_ordered_products}")


if __name__ == '__main__':
    main()
