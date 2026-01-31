import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from dependencies import get_current_user

client = TestClient(app)

# Mock data
mock_product = {
    "id": 1,
    "name": "Test Product",
    "description": "A test product",
    "price": 99.99,
    "stock": 10,
    "category_id": 1,
    "created_at": "2023-01-01T00:00:00Z",
}

# Mock user for authentication
mock_user = {"id": "test-user-id", "email": "test@example.com"}


@pytest.fixture
def mock_supabase():
    with patch("routers.products.supabase") as mock:
        yield mock


@pytest.fixture
def mock_auth():
    """Override the authentication dependency for tests"""

    def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


def test_get_products(mock_supabase):
    # Setup mock response
    mock_supabase.table.return_value.select.return_value.range.return_value.execute.return_value.data = [
        mock_product
    ]

    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Product"


def test_get_product_by_id(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        mock_product
    ]

    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Product"


def test_get_product_not_found(mock_supabase):
    mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = (
        []
    )

    response = client.get("/products/999")
    assert response.status_code == 404


def test_create_product(mock_supabase, mock_auth):
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
        mock_product
    ]

    new_product = {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "stock": 10,
        "category_id": 1,
    }

    response = client.post("/products/", json=new_product)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"
