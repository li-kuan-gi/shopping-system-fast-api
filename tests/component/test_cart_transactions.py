import concurrent.futures
from sqlalchemy.orm import sessionmaker
from src.shopping.service import CartService
from src.shopping.domain import Product, Cart
from src.shopping.domain import InsufficientStock


def test_cart_service_add_item_concurrency(test_engine, mock_user):
    """
    Test that concurrent calls to CartService.add_item correctly decrease stock
    and update cart quantity using database row-level locking.
    """
    # Setup thread-safe session factory
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Arrange: Create a product with 100 stock
    db = TestingSessionLocal()
    product_id = 777
    initial_stock = 100
    quantity_to_add = 1
    num_requests = 20

    product = Product(id=product_id, stock=initial_stock)
    db.add(product)
    db.commit()
    db.close()

    def add_item_job():
        # Each job gets its own session to simulate concurrent users
        session = TestingSessionLocal()
        try:
            service = CartService(session)
            service.add_item(mock_user.id, product_id, quantity_to_add)
        finally:
            session.close()

    # Act: Run concurrent service calls
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(add_item_job) for _ in range(num_requests)]
        concurrent.futures.wait(futures)

    # Assert: Verify all jobs finished without exceptions
    for future in futures:
        future.result()  # This will raise an exception if the job failed

    # Verify final state
    db = TestingSessionLocal()
    updated_product = db.query(Product).filter(Product.id == product_id).one()
    expected_stock = initial_stock - (num_requests * quantity_to_add)

    assert updated_product.stock == expected_stock

    cart = db.query(Cart).filter(Cart.user_id == mock_user.id).one()
    cart_item = next(item for item in cart.items if item.product_id == product_id)
    assert cart_item.quantity == num_requests * quantity_to_add

    db.close()


def test_cart_service_add_remove_alternating_concurrency(test_engine, mock_user):
    """
    Test that concurrent alternating add/remove calls correctly maintain state.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Arrange: Create a product
    db = TestingSessionLocal()
    product_id = 666
    initial_stock = 100
    db.add(Product(id=product_id, stock=initial_stock))
    db.commit()
    db.close()

    num_cycles = 10

    def alternating_job():
        session = TestingSessionLocal()
        try:
            service = CartService(session)
            service.add_item(mock_user.id, product_id, 2)
            service.remove_item(mock_user.id, product_id, 1)
        finally:
            session.close()

    # Act
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(alternating_job) for _ in range(num_cycles)]
        concurrent.futures.wait(futures)

    # Assert
    for future in futures:
        future.result()

    db = TestingSessionLocal()
    product = db.query(Product).filter(Product.id == product_id).one()
    cart = db.query(Cart).filter(Cart.user_id == mock_user.id).one()
    cart_item = next(item for item in cart.items if item.product_id == product_id)

    assert product.stock == initial_stock - num_cycles
    assert cart_item.quantity == num_cycles
    db.close()


def test_cart_service_rollback_on_failure(test_engine):
    """
    Test that if an operation fails (e.g. InsufficientStock),
    no changes are persisted to the database (rollback behavior).
    """

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    # Arrange: Create a product
    db = TestingSessionLocal()
    product_id = 444
    user_id = "rollback_user"
    initial_stock = 5
    db.add(Product(id=product_id, stock=initial_stock))
    db.commit()
    db.close()

    # Act: Try to add item but fail due to insufficient stock
    db = TestingSessionLocal()
    service = CartService(db)
    try:
        # This will:
        # 1. Start a transaction
        # 2. Insert a new Cart (uncommitted)
        # 3. Lock the Product
        # 4. Raise InsufficientStock
        # 5. Skip session.commit()
        service.add_item(user_id, product_id, 10)
    except InsufficientStock:
        pass
    finally:
        db.close()  # Implicitly rolls back because it wasn't committed

    # Assert: Verify that NO cart was created and stock remains unchanged
    db = TestingSessionLocal()
    product = db.query(Product).filter(Product.id == product_id).one()
    assert product.stock == initial_stock

    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    assert cart is None
    db.close()
