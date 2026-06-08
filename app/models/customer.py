from sqlalchemy import Column
from database import Base
from sqlalchemy import Integer,String,DateTime

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime)
