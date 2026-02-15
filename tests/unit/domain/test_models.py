import pytest
from src.models import Product, Cart, CartItem
from src.domain.exceptions import InsufficientStock, ItemNotFoundInCart


def test_product_initialization():
    product = Product(id=1, stock=10)
    assert product.id == 1
    assert product.stock == 10


def test_cart_add_item_success():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    cart.add_item(product, 2)

    assert len(cart.items) == 1
    assert cart.items[0].product_id == 1
    assert cart.items[0].quantity == 2
    assert product.stock == 8


def test_cart_add_existing_item_updates_quantity():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    cart.add_item(product, 2)
    cart.add_item(product, 3)

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5
    assert product.stock == 5


def test_cart_add_item_insufficient_stock():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=2)

    with pytest.raises(InsufficientStock):
        cart.add_item(product, 3)

    assert len(cart.items) == 0
    assert product.stock == 2


def test_cart_remove_item_success():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    cart.add_item(product, 5)

    cart.remove_item(product, 2)

    assert cart.items[0].quantity == 3
    assert product.stock == 7


def test_cart_remove_item_completely_removes_from_list():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    cart.add_item(product, 5)

    cart.remove_item(product, 5)

    assert len(cart.items) == 0
    assert product.stock == 10


def test_cart_remove_more_than_in_cart_removes_completely():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    cart.add_item(product, 5)

    # Even if we try to remove 10, it only has 5.
    # Logic in remove_item: actual_return = min(item.quantity, quantity)
    cart.remove_item(product, 10)

    assert len(cart.items) == 0
    assert product.stock == 10


def test_cart_remove_non_existent_item_raises_error():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    with pytest.raises(ItemNotFoundInCart):
        cart.remove_item(product, 1)
