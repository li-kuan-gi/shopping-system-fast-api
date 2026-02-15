from src.domain.exceptions import InsufficientStock, ItemNotFoundInCart


class Product:
    """Product domain model."""

    id: int
    stock: int

    def __init__(self, id: int, stock: int):
        self.id = id
        self.stock = stock

    def decrease_stock(self, quantity: int):
        if self.stock < quantity:
            raise InsufficientStock()
        self.stock -= quantity

    def increase_stock(self, quantity: int):
        self.stock += quantity


class CartItem:
    """Cart item domain model."""

    cart_id: int | None
    product_id: int | None
    quantity: int

    def __init__(
        self,
        cart_id: int | None = None,
        product_id: int | None = None,
        quantity: int = 0,
    ):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity


class Cart:
    """Cart aggregate root."""

    user_id: str
    items: list[CartItem]

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items = []

    def add_item(self, product: Product, quantity: int):
        """Add an item to the cart. Does NOT handle stock."""
        # Update existing item or add new
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += quantity
                return

        new_item = CartItem(product_id=product.id, quantity=quantity)
        self.items.append(new_item)

    def remove_item(self, product: Product, quantity: int) -> int:
        """
        Remove an item from the cart (or decrease quantity).
        Does NOT handle stock.
        Returns the actual quantity removed/returned.
        """
        for item in self.items:
            if item.product_id == product.id:
                actual_return = min(item.quantity, quantity)
                item.quantity -= quantity
                if item.quantity <= 0:
                    self.items.remove(item)
                return actual_return

        raise ItemNotFoundInCart()
