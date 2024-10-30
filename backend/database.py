from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///./data.db"

class Base(DeclarativeBase): pass
