from database import *
from sqlalchemy import  Column, Integer, String

class Flower(Base):
    __tablename__ = "flowers"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    cost = Column(Integer)
