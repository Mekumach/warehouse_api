from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Session, select
from typing import Annotated

from .models import Product, OrderItem, Order
from .schemas import ProductCreate, ProductRead, OrderCreate, OrderRead, OrderStatusUpdate
from .database import get_session, init_db

app = FastAPI()

SessionDep = Annotated[Session, Depends(get_session)]


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/products", response_model=ProductRead)
def create_product(product: ProductCreate, session: SessionDep):
    db_product = Product(**product.dict())

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@app.get("/products", response_model=list[ProductRead])
def get_products(session: SessionDep):
    products = session.exec(select(Product)).all()
    return products


@app.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.put("/products/{product_id}", response_model=ProductRead)
def update_product(product_id: int, product_data: ProductCreate, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for key, value in product_data.dict().items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: SessionDep):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()
    return {"message": "Product deleted"}


@app.post("/orders", response_model=OrderRead)
def create_order(order_data: OrderCreate, session: SessionDep):
    order = Order()

    for item_data in order_data.items:
        product = session.get(Product, item_data.product_id)
        if not product or product.quantity < item_data.quantity:
            raise HTTPException(status_code=400, detail="Not enough stock for product")

        product.quantity -= item_data.quantity
        order_item = OrderItem(product_id=item_data.product_id, quantity=item_data.quantity)
        order.items.append(order_item)

    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@app.get("/orders", response_model=list[OrderRead])
def get_orders(session: SessionDep):
    orders = session.exec(select(Order)).all()
    return orders


@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.patch("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(order_id: int, status_update: OrderStatusUpdate, session: SessionDep):
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
