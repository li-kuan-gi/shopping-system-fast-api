from sqlalchemy.orm import Session
from src.domain.services import add_item_to_cart, remove_item_from_cart
from src.repositories.cart import CartRepository
from src.repositories.product import ProductRepository
from src.services.exceptions import CartNotFound, ProductNotFound


class CartService:
    session: Session
    cart_repo: CartRepository
    product_repo: ProductRepository

    def __init__(self, session: Session):
        self.session = session
        self.cart_repo = CartRepository(session)
        self.product_repo = ProductRepository(session)

    def add_item(self, user_id: str, product_id: int, quantity: int):
        # 1. Optimistic Cart Fetch/Lock
        # Try to get the cart first (common case)
        cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        # If not found, create it (rare case)
        if not cart:
            self.cart_repo.create_if_not_exists(user_id)
            # Fetch again after creation
            cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        if not cart:
            raise CartNotFound("Failed to retrieve active cart")

        # 2. Lock Product first (to ensure stock consistency)
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            raise ProductNotFound(f"Product {product_id} not found")

        # 3. Use domain service
        add_item_to_cart(cart, product, quantity)
        self.session.commit()

    def remove_item(self, user_id: str, product_id: int, quantity: int):
        # 1. Fetch and Lock Cart
        cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        if not cart:
            raise CartNotFound("Item not found in cart")

        # 2. Lock Product
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            raise ProductNotFound(f"Product {product_id} not found")

        # 3. Use domain service
        remove_item_from_cart(cart, product, quantity)
        self.session.commit()
