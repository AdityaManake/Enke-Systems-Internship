from sqlalchemy import Column
from database import Base
from sqlalchemy import Integer,Numeric,ForeignKey


class OrderItem(Base):
    __tablename__ = 'order_items'
    id= Column(Integer, primary_key=True)
    order_id= Column(Integer, ForeignKey("orders.id"))
    product_id= Column(Integer, ForeignKey("products.id"))
    quantity= Column(Integer)
    total_price= Column(Numeric(10,2))