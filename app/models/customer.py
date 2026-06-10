from database import Base

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import func


class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime, server_default=func.now())
