from fastapi import FastAPI, status, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists, select
from flowers import *

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()
app = FastAPI()

@app.post("/flower")
async def add_flower(request: Request):
    data = await request.json()
    if (db.query(exists().where(Flower.title == data["title"])).scalar()):
        return JSONResponse(content = data, status_code=status.HTTP_409_CONFLICT)
    flower = Flower(title=data["title"], description=data["description"], cost=data["cost"])
    db.add(flower)
    db.commit()
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)

@app.get("/flower/{id}")
def get_flower(id):
    if (db.query(exists().where(Flower.id == id)).scalar() == False):
        return JSONResponse(content={}, status_code=status.HTTP_404_NOT_FOUND)
    data = db.get(Flower, id)
    flower = {"title" : data.title, "description": data.description, "cost": data.cost}
    return JSONResponse(content=flower, status_code=status.HTTP_200_OK)
