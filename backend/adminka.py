from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from admin import *
from flowers import *
from users import *
from db import *

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Добавление товара на сайт

class Product(BaseModel):
    id: int
    name: str
    description: str
    cost: float

@app.post("/add_product/")
async def add_product(product_id: int, db: Session = Depends(get_db)):
    new_product = Product(name = Product.name, description = Product.description, cost = Product.cost)
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {"message": "Товар добавлен на сайт", "product_id": Product.id}

#Удаление товара с сайта по id

@app.delete("/delete_product/")
async def delete_product(product_id: int):
    product_to_delete = db.query(Product).filter(Product.id == Product.id).first()
    if not product_to_delete:
        raise HTTPException(status_code=404, detail="Товар не найден")

    db.delete(product_to_delete)
    db.commit()

    return {"message": "Товар удалён"}

#Изменение цены товара

class UpdatePriceModel(BaseModel):
    new_price: float

@app.put("/update_product_price/{product_id}")
async def update_product_price(
    product_id: int,
    price_data: UpdatePriceModel,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    
    product.cost = price_data.new_price
    db.commit()
    db.refresh(product)

    return {"message": "Цена товара обновлена", "product_id": product.id, "new_price": product.cost}

#Изменение описания товара

class UpdateDescriptionModel(BaseModel):
    new_description: str

@app.put("/update_product_description/{product_id}")
async def update_product_description(
    product_id: int,
    description_data: UpdateDescriptionModel,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")

    product.description = description_data.new_description
    db.commit()
    db.refresh(product)

    return {
        "message": "Описание товара обновлено",
        "product_id": product.id,
        "new_description": product.description,
    }

#Добавление и удаление новых администраторов

class AdminCreate(BaseModel):
    username: str
    password: str

@app.post("/admins/", response_model=AdminCreate)
async def create_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = Admin(username=admin.username, password=admin.password)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

@app.delete("/admins/{admin_id}")
async def delete_admin(admin_id: int, db: Session = Depends(get_db)):
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        raise HTTPException(status_code=404, detail="Администратор не найден")

    db.delete(db_admin)
    db.commit()
