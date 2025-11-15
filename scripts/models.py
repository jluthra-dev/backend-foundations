#day 4
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
    orders: List['Order'] = Relationship(back_populates="user")

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    item: str
    amount: float
    user_id: int = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="orders")

class UserCreate(SQLModel):
    name: str
    email: str

class UserRead(SQLModel):
    id: int
    name: str
    email: str

class UserUpdate(SQLModel):
    name: Optional[str] = None
    email: Optional[str] = None

class OrderCreate(SQLModel):
    item: str
    amount: float
    user_id: int

class OrderRead(SQLModel):
    id: int
    item: str
    amount: float
    user_id: int

class OrderUpdate(SQLModel):
    item: Optional[str] = None
    amount: Optional[float] = None