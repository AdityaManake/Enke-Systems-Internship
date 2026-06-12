import logging
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import build_database_url

from sqlalchemy import create_engine
from sqlalchemy import text

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO)


def main():
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    charts_dir = os.path.join(queries_dir, "charts")
    dict_df = creating_df(queries_dir)
    customer_vs_amount(dict_df, charts_dir)
    product_vs_revenue(dict_df, charts_dir)
    orders_per_month(dict_df, charts_dir)
    ordervalue_vs_customers(dict_df, charts_dir)
    customer_vs_ordercount(dict_df, charts_dir)
    mostexpensive_orders(dict_df, charts_dir)
    products_never_ordered(dict_df)


def creating_df(queries_dir):
    database_url = build_database_url()
    engine = create_engine(database_url)

    df_dict = {}
    for file in os.listdir(queries_dir):
        logger.info(f"Loading queries from {file}")
        if file.endswith(".sql"):
            try:
                df_name = file.replace(".sql", "_df")
                result = run_query(engine, file)
                df_dict[df_name] = pd.DataFrame(result)
            except Exception as e:
                logger.error(f"{file}, error : {e}")
    return df_dict


def run_query(engine, filename: str):
    queries_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(queries_dir, filename)) as f:
        query = f.read()
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()


def customer_vs_amount(df_dict, chart_dir):
    top_customers = df_dict["top_customers_df"]
    labels = top_customers["id"].astype(str) + " - " + top_customers["name"]
    plt.bar(labels, top_customers.revenue, color="blue", width=0.6)
    plt.xlabel("Customers")
    plt.ylabel("Revenue")
    plt.legend()
    plt.savefig(os.path.join(chart_dir, "customer_vs_amount.png"))
    plt.close()


def product_vs_revenue(df_dict, chart_dir):
    top_products = df_dict["top_products_df"]
    labels = top_products["id"].astype(str) + " - " + top_products["name"]
    plt.bar(labels, top_products.total_revenue, color="blue", width=0.6)
    plt.xlabel("Products")
    plt.ylabel("Revenue")
    plt.legend()
    plt.savefig(os.path.join(chart_dir, "product_vs_revenue.png"))
    plt.close()


def orders_per_month(df_dict, chart_dir):
    order_per_month = df_dict["orders_per_month_df"]
    plt.plot(order_per_month.month, order_per_month.total_orders, color="blue")
    plt.xlabel("Month")
    plt.ylabel("Total Orders")
    plt.legend()
    plt.savefig(os.path.join(chart_dir, "orders_per_month.png"))
    plt.close()


def ordervalue_vs_customers(df_dict, chart_dir):
    avg_order_value = df_dict["avg_order_value_df"]
    plt.hist(avg_order_value.id, avg_order_value.average_order_value, color="blue")
    plt.xlabel("Customers")
    plt.ylabel("Average Order Value")
    plt.savefig(os.path.join(chart_dir, "ordervalue_vs_customers.png"))
    plt.close()


def customer_vs_ordercount(df_dict, chart_dir):
    customers_with_many_orders = df_dict["customers_with_many_orders_df"]
    plt.bar(customers_with_many_orders.id, customers_with_many_orders.total_orders, color="blue", width=0.6)
    plt.xlabel("Customers")
    plt.ylabel("Total Orders")
    plt.legend()
    plt.savefig(os.path.join(chart_dir, "customer_vs_ordercount.png"))
    plt.close()


def mostexpensive_orders(df_dict, chart_dir):
    most_expensive_order_per_customer = df_dict["most_expensive_order_per_customer_df"]
    plt.plot(most_expensive_order_per_customer.id, most_expensive_order_per_customer.most_expensive_order, color="blue")
    plt.xlabel("Customers")
    plt.ylabel("Most Expensive Orders")
    plt.legend()
    plt.savefig(os.path.join(chart_dir, "mostexpensive_order_per_customer.png"))
    plt.close()


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
