from sqlalchemy import create_engine, Numeric, ForeignKey
from sqlalchemy.orm import  DeclarativeBase
from sqlalchemy import Integer, String, Column, DateTime

class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = 'customers'
    id= Column(Integer, primary_key=True )
    name= Column(String)
    email= Column(String)
    created_at= Column(DateTime)


class Product(Base):
    __tablename__ = 'products'
    id= Column(Integer, primary_key=True)
    name= Column(String)
    price= Column(Numeric(10,2))
    created_at= Column(DateTime)


class Order(Base):
    __tablename__ = 'orders'
    id= Column(Integer, primary_key=True)
    customer_id= Column(Integer, ForeignKey("customers.id"))
    created_at= Column(DateTime)

class OrderItem(Base):
    __tablename__ = 'order_items'
    id= Column(Integer, primary_key=True)
    order_id= Column(Integer, ForeignKey("orders.id"))
    product_id= Column(Integer, ForeignKey("products.id"))
    quantity= Column(Integer)
    total_price= Column(Numeric(10,2))
    




