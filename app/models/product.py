from database import Base

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Numeric
from sqlalchemy import func


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
