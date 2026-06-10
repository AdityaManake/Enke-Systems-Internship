from database import Base

from sqlalchemy import Column
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy import func


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime, server_default=func.now())
