from database import *
from sqlalchemy import  Column, Integer, String

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String)
    password = Column(String)

