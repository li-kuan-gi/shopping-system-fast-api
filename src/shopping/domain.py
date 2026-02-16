class InsufficientStock(Exception):
    """Raised when a product does not have enough stock to fulfill a request."""

    pass


class ItemNotFoundInCart(Exception):
    """Raised when an item is expected in the cart but not found."""

    pass


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


def add_item_to_cart(cart: Cart, product: Product, quantity: int):
    """
    Domain service to add an item to the cart and decrease product stock.
    """
    product.decrease_stock(quantity)
    cart.add_item(product, quantity)


def remove_item_from_cart(cart: Cart, product: Product, quantity: int):
    """
    Domain service to remove an item from the cart and increase product stock.
    """
    actual_return = cart.remove_item(product, quantity)
    product.increase_stock(actual_return)
