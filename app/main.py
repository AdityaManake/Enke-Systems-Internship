import logging
import os
import random

from app.database import build_database_url
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_items import OrderItem
from app.models.product import Product
from faker import Faker
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
BATCH_SIZE = 5000


def main():
    database_url = build_database_url()
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    num_customers = int(os.getenv("NUM_CUSTOMERS", 500))
    num_products = int(os.getenv("NUM_PRODUCTS", 5000))
    num_orders = int(os.getenv("NUM_ORDERS", 50000))

    with Session() as session:
        customers = seed_customers(session, num_customers)
        products = seed_products_once(session, num_products)
        seed_orders(session, num_orders, products)


def seed_products_once(session, num_products):
    count = session.query(Product).count()
    if count == 0:
        seed_products(session, num_products)
        logger.info(f"no previous records found, thus inserted {num_products} products")
        return session.query(Product).all()
    else:
        logger.info(f"found {count} products in database so not appending")
        return session.query(Product).all()


def seed_customers(session, num_customers):
    fake = Faker()
    customers = []
    count = session.query(Customer).count()
    if count == 0: count = count + 1
    for i in range(num_customers):
        name = fake.name()
        name = (name.replace(" ", "")).lower()
        domain = ["gmail.com", "yahoo.com", "outlook.com"]
        customer = Customer(name=fake.name(), email=f"{name}{count}.{random.choice(domain)}")
        customers.append(customer)
        count = count + 1
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


def seed_orders(session, num_orders, products):
    customer_ids = [c[0] for c in session.query(Customer.id).all()]
    max_order_id = session.query(func.max(Order.id)).scalar() or 0
    next_order_id = max_order_id + 1
    order_batch = []
    order_items_batch = []

    for order_num in range(num_orders):
        customer_id = random.choice(customer_ids)
        order_id = next_order_id + order_num
        order_batch.append(
            {
                "id": order_id,
                "customer_id": customer_id,
            }
        )

        number_of_items = random.randint(1, 5)
        for _ in range(number_of_items):
            product = random.choice(products)
            quantity = random.randint(1, 5)
            total_price = product.price * quantity
            order_items_batch.append(
                {
                    "order_id": order_id,
                    "product_id": product.id,
                    "quantity": quantity,
                    "total_price": total_price,
                }
            )
        if len(order_batch) >= BATCH_SIZE:
            session.bulk_insert_mappings(Order, order_batch)
            order_batch.clear()

        if len(order_items_batch) >= BATCH_SIZE:
            session.bulk_insert_mappings(OrderItem, order_items_batch)
            order_items_batch.clear()
    if order_batch:
        session.bulk_insert_mappings(Order, order_batch)

    if order_items_batch:
        session.bulk_insert_mappings(OrderItem, order_items_batch)
    session.commit()
    logger.info(f"Inserted {num_orders} orders successfully")


if __name__ == "__main__":
    main()
