from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
from dotenv import load_dotenv
import hashlib

from flowers import *
from users import *
from auth import *

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

load_dotenv()
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autoflush=False, bind=engine)
db = SessionLocal()
app = FastAPI()

@app.post("/flower")
async def add_flower(request: Request):
    data = await request.json()
    if (db.query(exists().where(Flower.title == data["title"])).scalar()):
        return JSONResponse(content={"reason" : "flower with same title exists"}, status_code=status.HTTP_409_CONFLICT)
    flower = Flower(title=data["title"], description=data["description"], cost=data["cost"])
    db.add(flower)
    db.commit()
    return JSONResponse(content=data, status_code=status.HTTP_200_OK)

@app.get("/flower/{id}")
def get_flower(id):
    data = db.get(Flower, id)
    if data == None:
        return JSONResponse(content={"reason" : "flower is not exists"}, status_code=status.HTTP_404_NOT_FOUND)
    flower = {"title" : data.title, "description": data.description, "cost": data.cost}
    return JSONResponse(content=flower, status_code=status.HTTP_200_OK)

@app.post("/sign_up")
async def sign_in(request: Request):
    data = await request.json()
    if (db.query(exists().where(User.login == data["login"])).scalar()):
        return JSONResponse(content={"reason" : "user with same login exists"}, status_code=status.HTTP_409_CONFLICT)
    user = User(login=data["login"], password=hashlib.sha256(data["password"].encode("utf-8")).hexdigest())
    db.add(user)
    db.commit()
    return JSONResponse(content={"login" : data["login"]}, status_code=status.HTTP_201_CREATED)

@app.post("/sign_in")
async def sign_in(request: Request, response: Response):
    data = await request.json()
    user = db.query(User).filter(User.password == hashlib.sha256(data["password"].encode("utf-8")).hexdigest()).filter(User.login == data["login"]).one_or_none()
    if user == None or user.login != data["login"]:
        return JSONResponse(content={"reason" : "wrong password or login"}, status_code=status.HTTP_401_UNAUTHORIZED)
    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie(key="users_access_token", value=access_token, httponly=True)
    return JSONResponse(content={"status" : "ok"}, status_code=status.HTTP_200_OK)

# @app.get("/me")
# def get_me(user_data: User = Depends(get_current_user)):
#     return    