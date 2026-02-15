"""
Component tests for the cart router.

These tests use a real Postgres database running in Docker to verify
the cart endpoints work correctly with actual database operations.
"""

from src.models import Product, Cart, CartItem


class TestAddItemToCart:
    """Tests for the /cart/add-item endpoint."""

    def test_add_item_successfully(self, client, db_session, mock_user):
        """Test successfully adding an item to the cart."""
        # Create a test product
        product = Product(id=1, stock=10)
        db_session.add(product)
        db_session.commit()

        # Add item to cart
        response = client.post("/cart/add-item", json={"product_id": 1, "quantity": 2})

        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Item added to cart"}

        # Verify cart was created and item exists
        cart = db_session.query(Cart).filter(Cart.user_id == mock_user.id).first()
        assert cart is not None
        assert len(cart.items) == 1
        assert cart.items[0].product_id == 1
        assert cart.items[0].quantity == 2

        # Verify product stock was decreased
        db_session.refresh(product)
        assert product.stock == 8

    def test_add_item_product_not_exists(self, client, db_session):
        """Test adding a non-existent product to cart."""
        response = client.post(
            "/cart/add-item", json={"product_id": 999, "quantity": 1}
        )

        assert response.status_code == 404
        assert "product" in response.json()["detail"].lower()
        assert "not found" in response.json()["detail"].lower()

        # Verify no cart item was created
        cart_items = db_session.query(CartItem).all()
        assert len(cart_items) == 0

    def test_add_item_not_authenticated(self, unauthenticated_client, db_session):
        """Test adding item without authentication."""
        # Create a test product
        product = Product(id=1, stock=10)
        db_session.add(product)
        db_session.commit()

        # Try to add item without auth
        response = unauthenticated_client.post(
            "/cart/add-item", json={"product_id": 1, "quantity": 1}
        )

        assert response.status_code == 401


class TestRemoveItemFromCart:
    """Tests for the /cart/remove-item endpoint."""

    def test_remove_item_successfully(self, client, db_session, mock_user):
        """Test successfully removing an item from the cart."""
        # Create a test product, cart, and cart item
        product = Product(id=1, stock=5)
        db_session.add(product)

        cart = Cart(user_id=mock_user.id)
        db_session.add(cart)
        db_session.commit()

        cart_item = CartItem(cart_id=cart.id, product_id=1, quantity=3)
        db_session.add(cart_item)
        db_session.commit()

        # Remove item from cart
        response = client.post(
            "/cart/remove-item", json={"product_id": 1, "quantity": 1}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "success"

        # Verify cart item quantity was decreased
        db_session.refresh(cart_item)
        assert cart_item.quantity == 2

        # Verify product stock was increased
        db_session.refresh(product)
        assert product.stock == 6

    def test_remove_item_not_in_cart(self, client, db_session):
        """Test removing an item that's not in the cart."""
        # Create a test product but no cart item
        product = Product(id=1, stock=10)
        db_session.add(product)
        db_session.commit()

        response = client.post(
            "/cart/remove-item", json={"product_id": 1, "quantity": 1}
        )

        assert response.status_code == 404
        assert "Item not found in cart" in response.json()["detail"]

    def test_remove_item_not_authenticated(
        self, unauthenticated_client, db_session, mock_user
    ):
        """Test removing item without authentication."""
        # Create a test product, cart and cart item
        product = Product(id=1, stock=5)
        db_session.add(product)

        cart = Cart(user_id=mock_user.id)
        db_session.add(cart)
        db_session.commit()

        cart_item = CartItem(cart_id=cart.id, product_id=1, quantity=2)
        db_session.add(cart_item)
        db_session.commit()

        # Try to remove item without auth
        response = unauthenticated_client.post(
            "/cart/remove-item", json={"product_id": 1, "quantity": 1}
        )

        assert response.status_code == 401
