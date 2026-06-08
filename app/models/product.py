from sqlalchemy import Column
from database import Base
from sqlalchemy import Integer,String,DateTime,Numeric

class Product(Base):
    __tablename__ = 'products'
    id= Column(Integer, primary_key=True)
    name= Column(String)
    price= Column(Numeric(10,2))
    created_at= Column(DateTime)