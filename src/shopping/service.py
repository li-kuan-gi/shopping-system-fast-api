import logging
from sqlalchemy.orm import Session
from src.shopping.domain import add_item_to_cart, remove_item_from_cart
from src.shopping.repository import CartRepository, ProductRepository

logger = logging.getLogger(__name__)


class CartNotFound(Exception):
    pass


class ProductNotFound(Exception):
    pass


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
        logger.debug(f"Attempting to fetch/lock cart for user {user_id}")
        cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        # If not found, create it (rare case)
        if not cart:
            logger.info(f"Cart not found for user {user_id}. Creating new cart.")
            self.cart_repo.create_if_not_exists(user_id)
            # Fetch again after creation
            cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        if not cart:
            logger.error(f"Failed to retrieve or create cart for user {user_id}")
            raise CartNotFound("Failed to retrieve active cart")

        # 2. Lock Product first (to ensure stock consistency)
        logger.debug(f"Locking product {product_id} for stock validation")
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            logger.warning(f"Product {product_id} not found during add_item")
            raise ProductNotFound(f"Product {product_id} not found")

        # 3. Use domain service
        logger.info(f"Applying domain logic: adding product {product_id} to cart")
        add_item_to_cart(cart, product, quantity)

        logger.debug("Committing transaction for add_item")
        self.session.commit()
        logger.info(f"Successfully committed add_item for user {user_id}")

    def remove_item(self, user_id: str, product_id: int, quantity: int):
        # 1. Fetch and Lock Cart
        logger.debug(f"Fetching/locking cart for user {user_id} during removal")
        cart = self.cart_repo.get_by_user_id_with_lock(user_id)

        if not cart:
            logger.warning(
                f"Attempted to remove item from non-existent cart for user {user_id}"
            )
            raise CartNotFound("Item not found in cart")

        # 2. Lock Product
        logger.debug(f"Locking product {product_id} during removal")
        product = self.product_repo.get_by_id_with_lock(product_id)

        if not product:
            logger.warning(f"Product {product_id} not found during remove_item")
            raise ProductNotFound(f"Product {product_id} not found")

        # 3. Use domain service
        logger.info(f"Applying domain logic: removing product {product_id} from cart")
        remove_item_from_cart(cart, product, quantity)

        logger.debug("Committing transaction for remove_item")
        self.session.commit()
        logger.info(f"Successfully committed remove_item for user {user_id}")
