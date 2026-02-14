import concurrent.futures
from src.models import Product, CartItem


def test_add_item_concurrency(client, db_session, mock_user):
    """
    Test that concurrent requests to add items to cart correctly decrease stock.
    This test aims to reproduce a race condition where multiple threads read the
    same stock value before any of them update it.
    """
    # Arrange: Create a product with 100 stock
    product_id = 1
    initial_stock = 100
    quantity_to_add = 1
    num_requests = 20

    product = Product(id=product_id, stock=initial_stock)
    db_session.add(product)
    db_session.commit()

    # Act: Send multiple concurrent requests to add 1 item each
    def add_item():
        # Note: We use a fresh client/session per thread conceptually,
        # but FastAPI TestClient is synchronous and uses the app's dependency overrides.
        # In a real environment, these would be separate HTTP requests.
        return client.post(
            "/cart/add-item",
            json={"product_id": product_id, "quantity": quantity_to_add},
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_item) for _ in range(num_requests)]
        responses = [f.result() for f in futures]

    # Assert: Verify all requests were successful
    for response in responses:
        assert response.status_code == 200

    # Verify final stock: Should be exactly initial_stock - (num_requests * quantity_to_add)
    db_session.expire_all()
    updated_product = db_session.query(Product).filter(Product.id == product_id).one()

    expected_stock = initial_stock - (num_requests * quantity_to_add)

    print(f"Initial stock: {initial_stock}")
    print(f"Requests: {num_requests} x {quantity_to_add}")
    print(f"Final stock: {updated_product.stock}")
    print(f"Expected stock: {expected_stock}")

    assert (
        updated_product.stock == expected_stock
    ), f"Race condition detected! Final stock {updated_product.stock} != expected {expected_stock}"

    # Also verify CartItem quantity
    cart_item = (
        db_session.query(CartItem)
        .filter(CartItem.user_id == mock_user.id, CartItem.product_id == product_id)
        .one()
    )
    assert cart_item.quantity == num_requests * quantity_to_add
