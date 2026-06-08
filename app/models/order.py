from sqlalchemy import Column
from app.database import Base
from sqlalchemy import Integer,ForeignKey,DateTime

class Order(Base):
    __tablename__ = 'orders'
    id= Column(Integer, primary_key=True)
    customer_id= Column(Integer, ForeignKey("customers.id"))
    created_at= Column(DateTime)
