from fastapi import Response
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.sql import exists
from dotenv import load_dotenv
import hashlib

from flowers import *
from users import *
from auth import *
from db import *

load_dotenv()

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

@app.get("/me")
def get_me(user_data: User = Depends(get_current_user)):
    return get_current_user()

@app.get("/cart")
async def list_cart(current_user: User = Depends(get_current_user)):
    # Fetch all cart items for the user, including flower details
    cart_items = (
        db.query(CartItem)
        .options(joinedload(CartItem.flower))  # Use joinedload to retrieve flower details with the cart item
        .filter(CartItem.userId == current_user.id)
        .all()
    )

    # Format the response data
    cart_data = [
        {
            "flower_id": item.flowerId,
            "title": item.flower.title,
            "description": item.flower.description,
            "cost": item.flower.cost,
            "quantity": item.qty,
        }
        for item in cart_items
    ]
    return JSONResponse(content={"cart": cart_data}, status_code=status.HTTP_200_OK)


@app.post("/cart")
async def add_to_cart(flower_id: int, qty: int, current_user: User = Depends(get_current_user)):
    # Check if the flower exists
    flower = db.get(Flower, flower_id)
    if flower is None:
        return JSONResponse(content={"reason": "Flower not found"}, status_code=status.HTTP_404_NOT_FOUND)

    # Check if item already in cart; if so, update quantity
    cart_item = db.query(CartItem).filter(CartItem.userId == current_user.id,
                                          CartItem.flowerId == flower_id).one_or_none()
    if cart_item:
        cart_item.qty += qty
    else:
        cart_item = CartItem(userId=current_user.id, flowerId=flower_id, qty=qty)
        db.add(cart_item)

    db.commit()
    return JSONResponse(content={"status": "Item added to cart"}, status_code=status.HTTP_201_CREATED)


@app.delete("/cart")
async def remove_from_cart(flower_id: int, qty: int, current_user: User = Depends(get_current_user)):
    # Find the cart item for the user and flower
    cart_item = db.query(CartItem).filter(CartItem.userId == current_user.id,
                                          CartItem.flowerId == flower_id).one_or_none()
    if cart_item is None:
        return JSONResponse(content={"reason": "Cart item not found"}, status_code=status.HTTP_404_NOT_FOUND)

    # Check if the quantity to remove is valid
    if qty >= cart_item.qty:
        # If the quantity to remove is equal or more than the current quantity, delete the item
        db.delete(cart_item)
    else:
        # Otherwise, just reduce the quantity
        cart_item.qty -= qty

    db.commit()
    return JSONResponse(content={"status": "Item removed from cart"}, status_code=status.HTTP_200_OK)

