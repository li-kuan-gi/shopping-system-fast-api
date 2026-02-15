from src.domain.models import Cart, Product


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
