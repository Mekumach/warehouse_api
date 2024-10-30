from pydantic import BaseModel
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int


class ProductRead(ProductCreate):
    id: int


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]


class OrderRead(BaseModel):
    id: int
    created_at: datetime
    status: str
    items: list[OrderItemCreate]


class OrderStatusUpdate(BaseModel):
    status: str
