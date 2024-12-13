from database import *
from sqlalchemy import  Column, Integer, String

class CartItem(Base):
    __tablename__ = "cartItems"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer)  # FK
    flowerId = Column(Integer)  # FK
    qty = Column(Integer)
