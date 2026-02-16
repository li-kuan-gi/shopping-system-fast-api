import pytest
from src.shopping.domain import Product, InsufficientStock
from src.shopping.domain import (
    Cart,
    CartItem,
    ItemNotFoundInCart,
    add_item_to_cart,
    remove_item_from_cart,
)


def test_product_initialization():
    product = Product(id=1, stock=10)
    assert product.id == 1
    assert product.stock == 10


def test_product_decrease_stock():
    product = Product(id=1, stock=10)
    product.decrease_stock(2)
    assert product.stock == 8


def test_product_decrease_stock_insufficient():
    product = Product(id=1, stock=1)
    with pytest.raises(InsufficientStock):
        product.decrease_stock(2)


def test_product_increase_stock():
    product = Product(id=1, stock=10)
    product.increase_stock(2)
    assert product.stock == 12


def test_cart_add_item_success():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    cart.add_item(product, 2)

    assert len(cart.items) == 1
    assert cart.items[0].product_id == 1
    assert cart.items[0].quantity == 2
    # Product stock should NOT change here
    assert product.stock == 10


def test_cart_add_existing_item_updates_quantity():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    cart.add_item(product, 2)
    cart.add_item(product, 3)

    assert len(cart.items) == 1
    assert cart.items[0].quantity == 5


def test_cart_remove_item_success():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    cart.add_item(product, 5)

    cart.remove_item(product, 2)

    assert cart.items[0].quantity == 3
    # Product stock should NOT change here
    assert product.stock == 10


def test_cart_remove_item_completely_removes_from_list():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    cart.add_item(product, 5)

    cart.remove_item(product, 5)

    assert len(cart.items) == 0


def test_cart_remove_non_existent_item_raises_error():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    with pytest.raises(ItemNotFoundInCart):
        cart.remove_item(product, 1)


def test_add_item_to_cart_service():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)

    add_item_to_cart(cart, product, 3)

    assert product.stock == 7
    assert len(cart.items) == 1
    assert cart.items[0].quantity == 3


def test_remove_item_from_cart_service():
    cart = Cart(user_id="user1")
    product = Product(id=1, stock=10)
    add_item_to_cart(cart, product, 5)  # stock 5, cart 5

    remove_item_from_cart(cart, product, 3)  # stock 8, cart 2

    assert product.stock == 8
    assert cart.items[0].quantity == 2
