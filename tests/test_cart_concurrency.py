import concurrent.futures
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.dependencies import get_current_user
from src.models import Product, Cart, CartItem


def test_add_item_concurrency(test_engine, mock_user):
    """
    Test that concurrent requests to add items to cart correctly decrease stock.
    This test uses separate database sessions for each request to correctly
    simulate concurrent users and test the database row-level locking.
    """
    # Setup thread-safe session factory from the test_engine
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Dependency overrides: provide a FRESH session for each request
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        # Arrange: Create a product with 100 stock
        db = TestingSessionLocal()
        product_id = 999  # Use a unique ID for this test
        initial_stock = 100
        quantity_to_add = 1
        num_requests = 20

        product = Product(id=product_id, stock=initial_stock)
        db.add(product)
        db.commit()
        db.close()

        # Act: Send multiple concurrent requests using ThreadPoolExecutor
        def add_item_request(client):
            return client.post(
                "/cart/add-item",
                json={"product_id": product_id, "quantity": quantity_to_add},
            )

        with TestClient(app) as client:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                # Use executor.map to run requests in parallel
                responses = list(
                    executor.map(
                        lambda _: add_item_request(client), range(num_requests)
                    )
                )

        # Assert: Verify all requests were successful
        for response in responses:
            assert (
                response.status_code == 200
            ), f"Request failed: {response.status_code} - {response.text}"

        # Verify final stock: Should be exactly initial_stock - (num_requests * quantity_to_add)
        db = TestingSessionLocal()
        updated_product = db.query(Product).filter(Product.id == product_id).one()

        expected_stock = initial_stock - (num_requests * quantity_to_add)
        print(f"Final stock: {updated_product.stock}, Expected: {expected_stock}")

        assert (
            updated_product.stock == expected_stock
        ), f"Race condition! Final stock {updated_product.stock} != expected {expected_stock}"

        # Also verify CartItem quantity
        cart = db.query(Cart).filter(Cart.user_id == mock_user.id).one()
        cart_item = next(item for item in cart.items if item.product_id == product_id)

        assert cart_item.quantity == num_requests * quantity_to_add
        db.close()

    finally:
        # Cleanup overrides
        app.dependency_overrides.clear()


def test_add_remove_alternating_concurrency(test_engine, mock_user):
    """
    Test that concurrent alternating requests to add and remove items
    correctly maintain stock and cart quantity, preventing StaleDataError.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        # Arrange: Create a product
        db = TestingSessionLocal()
        product_id = 888
        initial_stock = 100
        db.add(Product(id=product_id, stock=initial_stock))
        db.commit()
        db.close()

        num_cycles = 10

        def alternating_ops(client):
            # Add 2 items, then remove 1 item
            r1 = client.post(
                "/cart/add-item", json={"product_id": product_id, "quantity": 2}
            )
            r2 = client.post(
                "/cart/remove-item", json={"product_id": product_id, "quantity": 1}
            )
            return [r1, r2]

        with TestClient(app) as client:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = list(
                    executor.map(lambda _: alternating_ops(client), range(num_cycles))
                )

        # Assert: All requests should succeed (no StaleDataError / 500)
        for op_results in results:
            for response in op_results:
                assert (
                    response.status_code == 200
                ), f"Request failed: {response.status_code} - {response.text}"

        # Verify final state
        # Net change per cycle: +2 added, -1 removed = +1 in cart, -1 in stock
        # Total change: +10 in cart, -10 in stock
        db = TestingSessionLocal()
        product = db.query(Product).filter(Product.id == product_id).one()

        cart = db.query(Cart).filter(Cart.user_id == mock_user.id).one()
        cart_item = next(item for item in cart.items if item.product_id == product_id)

        assert product.stock == initial_stock - num_cycles
        assert cart_item.quantity == num_cycles
        db.close()

    finally:
        app.dependency_overrides.clear()
