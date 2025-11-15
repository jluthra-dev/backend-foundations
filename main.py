from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import select, col
from contextlib import asynccontextmanager
from database import get_session, init_db
from typing import List
from models import *
from pathlib import Path

@asynccontextmanager
async def on_startup(app: FastAPI):
    init_db()
    print("DB path:", Path("./app.db").resolve())
    try:
        yield
    finally:
        print("shutdown")

app = FastAPI(title="User & Orders API- Day 4", lifespan=on_startup)

@app.get("/health")
def health(session=Depends(get_session)):
    session.exec(select(1)).one()
    return {"status": "ok"}

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, session=Depends(get_session)):
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(name=payload.name, email=payload.email)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users", response_model=List[UserRead])
def list_users(
    email: Optional[str] = None,
    name_contains: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    session=Depends(get_session)):
    stmt = select(User)

    if email:
        stmt = stmt.where(User.email == email)
    
    if name_contains:
        like = f"%{name_contains}"
        stmt = stmt.where(col(User.name).like(like))
    
    stmt = stmt.order_by(User.id).limit(limit).offset(offset)
    users = session.exec(select(User).order_by(User.id)).all()
    return users

@app.put("users/{user_id}", response_model=UserRead)
def replace_user(user_id: int, payload: UserCreate, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    other = session.exec(select(User).where(User.email == payload.email, User.id != user_id)).first()
    if other:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user.name = payload.name
    user.email = payload.email
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if payload.email is not None:
        other = session.exec(select(User).where(User.email == payload.email, User.id != user.id)).first()
        if other:
            raise HTTPException(status_code=400, detail="Email already exists")

    if payload.name is not None:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email

    session.add(user)
    session.commit()
    session.refresh(user)      
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session=Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return

@app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, session=Depends(get_session)):
    user = session.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=400, detail="User id does not exist")
    
    order = Order(item=payload.item, amount=payload.amount, user_id=payload.user_id)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@app.get("/orders", response_model=List[OrderRead])
def list_orders(
    user_id: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    session=Depends(get_session)):
    stmt = select(Order)
    
    if user_id is not None:
        stmt = stmt.where(Order.user_id == user_id)
    
    if min_amount is not None:
        stmt = stmt.where(Order.amount >= min_amount)

    if max_amount is not None:
        stmt = stmt.where(Order.amont <= max_amount)
    
    stmt = stmt.order_by(Order.id).limit(limit).offset(offset)
    orders = session.exec(stmt).all()
    return orders

@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session=Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.put("/orders/{order_id}", response_model=OrderRead)
def replace_order(order_id: int, payload: OrderCreate, session=Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not session.get(User, payload.user_id):
        raise HTTPException(status_code=400, detail="User id does not exist")
    
    order.item = payload.item
    order.amount = payload.amount
    order.user_id = payload.user_id
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@app.patch("/orders/{order_id}", response_model=OrderRead)
def update_order(order_id: int, payload: OrderUpdate, session=Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if payload.item is not None:
        order.item = payload.item
    if payload.amount is not None:
        order.amount = payload.amount
    
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

@app.delete("/orders/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, session=Depends(get_session)):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    session.delete(order)
    session.commit()
    return