import logging
import os
import random

from faker import Faker
from models.customer import Customer
from models.order import Order
from models.order_items import OrderItem
from models.product import Product
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    num_customers = int(os.getenv("NUM_CUSTOMERS", 500))
    num_products = int(os.getenv("NUM_PRODUCTS", 5000))
    num_orders = int(os.getenv("NUM_ORDERS", 50000))

    with Session() as session:
        customers = seed_customers(session, num_customers)
        products = seed_products(session, num_products)
        seed_orders(session, num_orders, customers, products)


def build_database_url() -> str:
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    return f"postgresql+psycopg2://"f"{db_user}:{db_password}@"f"{db_host}:{db_port}/{db_name}"


def seed_customers(session, num_customers):
    fake = Faker()
    customers = []
    for i in range(num_customers):
        customer = Customer(name=fake.name(), email=fake.unique.email())
        customers.append(customer)
    session.bulk_save_objects(customers, return_defaults=True)
    session.commit()
    logger.info(f"inserted {num_customers} customers")
    return customers


def seed_products(session, num_products):
    product_names = ["Keyboard", "Mouse", "Monitor", "Laptop", "Speaker", "Console", "Headphones", "SSD", "Charger"]
    brands = ["Logitech", "Dell", "HP", "Lenovo", "Samsung", "MSI", "Apple", "Acer"]
    products = []
    for i in range(num_products):
        product = Product(name=f"{random.choice(brands)}  {random.choice(product_names)}",
                          price=round(random.uniform(10, 10000), 2))
        products.append(product)
    session.bulk_save_objects(products, return_defaults=True)
    session.commit()
    logger.info(f"inserted {num_products} products")
    return products


def seed_orders(session, num_orders, customers, products):
    for order_num in range(num_orders):
        customer = random.choice(customers)
        order = Order(customer_id=customer.id)
        session.add(order)
        session.flush()
        number_of_items = random.randint(1, 5)
        for i in range(number_of_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            total_price = product.price * quantity
            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, total_price=total_price)
            session.add(order_item)
        if order_num % 1000 == 0:
            session.commit()
            logger.info(f"inserted {num_orders} orders")
    session.commit()


if __name__ == "__main__":
    main()
