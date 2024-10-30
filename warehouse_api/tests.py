import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from .main import app

# Создаем тестовую базу данных SQLite в памяти
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=False)

# Тестовый клиент для взаимодействия с FastAPI
client = TestClient(app)


# Функция для создания таблиц в тестовой базе
def setup_db():
    SQLModel.metadata.create_all(engine)


# Фикстура для использования тестовой базы данных в каждом тесте
@pytest.fixture(scope="function", autouse=True)
def db_session():
    # Создаем новую сессию для каждого теста
    setup_db()
    with Session(engine) as session:
        yield session
    # Удаляем все таблицы после теста
    SQLModel.metadata.drop_all(engine)


# Тест создания товара
def test_create_product():
    product_data = {
        "name": "Table",
        "description": "Wooden table",
        "price": 200.0,
        "quantity": 10
    }
    response = client.post("/products", json=product_data)
    product_id = response.json()["id"]
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Table"
    assert data["description"] == "Wooden table"
    assert data["price"] == 200.0
    assert data["quantity"] == 10
    assert data["id"] == product_id


# Тест получения списка товаров
def test_get_products():
    # Сначала добавляем товар
    product_data = {
        "name": "Chair",
        "description": "Comfortable chair",
        "price": 50.0,
        "quantity": 30
    }
    client.post("/products", json=product_data)

    # Проверяем список товаров
    response = client.get("/products")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[1]["name"] == "Chair"
    assert data[1]["description"] == "Comfortable chair"
    assert data[1]["price"] == 50.0
    assert data[1]["quantity"] == 30


# Тест получения товара по ID
def test_get_product_by_id():
    product_data = {
        "name": "Lamp",
        "description": "LED lamp",
        "price": 25.0,
        "quantity": 100
    }
    # Создаем товар
    response = client.post("/products", json=product_data)
    product_id = response.json()["id"]

    # Получаем товар по его ID
    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Lamp"
    assert data["description"] == "LED lamp"
    assert data["price"] == 25.0
    assert data["quantity"] == 100


# Тест обновления товара
def test_update_product():
    product_data = {
        "name": "Sofa",
        "description": "Leather sofa",
        "price": 500.0,
        "quantity": 5
    }
    # Создаем товар
    response = client.post("/products", json=product_data)
    product_id = response.json()["id"]

    # Обновляем информацию о товаре
    updated_product_data = {
        "name": "Sofa XL",
        "description": "Large leather sofa",
        "price": 600.0,
        "quantity": 3
    }
    response = client.put(f"/products/{product_id}", json=updated_product_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Sofa XL"
    assert data["description"] == "Large leather sofa"
    assert data["price"] == 600.0
    assert data["quantity"] == 3


# Тест создания заказа
def test_create_order():
    # Сначала добавляем товар
    product_data = {
        "name": "TV",
        "description": "Smart TV",
        "price": 1000.0,
        "quantity": 20
    }
    product_response = client.post("/products", json=product_data)
    product_id = product_response.json()["id"]

    # Создаем заказ
    order_data = {
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "processing"
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2


# Тест объявления ошибки при создании заказа при недостатке товара
def test_error_create_order():
    product_data = {
        "name": "Iphone",
        "description": "13",
        "price": 10000,
        "quantity": 1
    }
    product_response = client.post("/products", json=product_data)
    product_id = product_response.json()["id"]

    order_data = {
        "items": [
            {
                "product_id": product_id,
                "quantity": 2
            }
        ]
    }
    response = client.post("/orders", json=order_data)
    assert response.status_code == 400


# Тест обновления статуса заказа
def test_update_order_status():
    # Сначала добавляем товар
    product_data = {
        "name": "Fridge",
        "description": "Large fridge",
        "price": 1200.0,
        "quantity": 10
    }
    product_response = client.post("/products", json=product_data)
    product_id = product_response.json()["id"]

    # Создаем заказ
    order_data = {
        "items": [
            {
                "product_id": product_id,
                "quantity": 1
            }
        ]
    }
    order_response = client.post("/orders", json=order_data)
    order_id = order_response.json()["id"]

    # Обновляем статус заказа
    response = client.patch(f"/orders/{order_id}/status", json={"status": "shipped"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "shipped"
