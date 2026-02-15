class InsufficientStock(Exception):
    """Raised when a product does not have enough stock to fulfill a request."""

    pass


class ItemNotFoundInCart(Exception):
    """Raised when an item is expected in the cart but not found."""

    pass
