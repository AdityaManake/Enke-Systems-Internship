import os
from sqlalchemy import create_engine, text
import time
from sqlalchemy.orm import sessionmaker
from faker import Faker
from model import Customer, Product, Order, OrderItem
import random

fake= Faker()
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("Waiting for PostGreSQL...")
time.sleep(15)
print(f"Connecting to {DB_HOST}:{DB_PORT}")

engine = create_engine(DATABASE_URL)

Session= sessionmaker(bind=engine)
session = Session()
for i in range(500):
    customer = Customer(name=fake.name(),email=fake.unique.email())
    session.add(customer)
session.commit()
print("Inserted Customer details")

product_names=["Keyboard","Mouse","Monitor","Laptop","Speaker","Console","Headphones","SSD","Charger"]
brands = ["Logitech","Dell","HP","Lenovo","Samsung","MSI","Apple","Acer"]
for i in range(5000):
    product = Product(name=f"{random.choice(brands)}  {random.choice(product_names)}",price= round(random.uniform(10,10000),2))
    session.add(product)
session.commit()
print("Inserted Product Details")

customers = session.query(Customer).all()
products = session.query(Product).all()

for order_num in range(50000):
    customer = random.choice(customers)
    order = Order(customer_id=customer.id)
    session.add(order)
    session.flush()
    number_of_items = random.randint(1,5)
    for i in range(number_of_items):
        product = random.choice(products)
        quantity = random.randint(1,5)
        total_price = product.price * quantity
        order_item = OrderItem(order_id=order.id,product_id=product.id,quantity=quantity,total_price=total_price)
        session.add(order_item)
    if order_num % 1000 == 0:
        session.commit()
        print(f"Inserted {order_num} orders")
session.commit()





