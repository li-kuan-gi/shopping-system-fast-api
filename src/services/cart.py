from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.repositories.cart import CartRepository
from src.repositories.product import ProductRepository


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
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve active cart",
            )

        # 2. Lock Product first (to ensure stock consistency)
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # 3. Use aggregate logic
            cart.add_item(product, quantity)
            self.session.commit()
        except ValueError as e:
            self.session.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def remove_item(self, user_id: str, product_id: int, quantity: int):
        # 1. Fetch and Lock Cart
        cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        if not cart:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        # 2. Lock Product
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        try:
            # 3. Use aggregate logic
            cart.remove_item(product, quantity)
            self.session.commit()
        except ValueError as e:
            self.session.rollback()
            raise HTTPException(status_code=404, detail=str(e))
