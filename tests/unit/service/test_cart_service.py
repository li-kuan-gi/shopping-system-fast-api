import pytest
from unittest.mock import MagicMock, patch
from src.shopping.service import CartService, CartNotFound, ProductNotFound
from src.shopping.domain import Cart, Product


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def cart_service(mock_session):
    service = CartService(mock_session)
    # Mock the repository methods
    service.cart_repo.get_by_user_id_with_lock = MagicMock()
    service.cart_repo.create_if_not_exists = MagicMock()
    service.product_repo.get_by_id_with_lock = MagicMock()
    service.product_repo.get_by_id = MagicMock()
    return service


@patch("src.shopping.service.add_item_to_cart")
def test_add_item_success(mock_add_item, cart_service, mock_session):
    # Setup
    user_id = "user1"
    product_id = 1
    quantity = 2

    mock_cart = MagicMock(spec=Cart)
    mock_product = MagicMock(spec=Product)

    cart_service.cart_repo.get_by_user_id_with_lock.return_value = mock_cart
    cart_service.product_repo.get_by_id_with_lock.return_value = mock_product

    # Act
    cart_service.add_item(user_id, product_id, quantity)

    # Assert
    mock_add_item.assert_called_once_with(mock_cart, mock_product, quantity)
    mock_session.commit.assert_called_once()


@patch("src.shopping.service.add_item_to_cart")
def test_add_item_cart_not_found_initially_creates_it(
    mock_add_item, cart_service, mock_session
):
    # Setup
    user_id = "user1"
    product_id = 1

    mock_cart = MagicMock(spec=Cart)
    mock_product = MagicMock(spec=Product)

    # First call returns None, second call returns mock_cart
    cart_service.cart_repo.get_by_user_id_with_lock.side_effect = [None, mock_cart]
    cart_service.product_repo.get_by_id_with_lock.return_value = mock_product

    # Act
    cart_service.add_item(user_id, product_id, 1)

    # Assert
    cart_service.cart_repo.create_if_not_exists.assert_called_once_with(user_id)
    assert cart_service.cart_repo.get_by_user_id_with_lock.call_count == 2


def test_add_item_product_not_found_raises_error(cart_service):
    # Setup
    cart_service.cart_repo.get_by_user_id_with_lock.return_value = MagicMock(spec=Cart)
    cart_service.product_repo.get_by_id_with_lock.return_value = None

    # Act & Assert
    with pytest.raises(ProductNotFound):
        cart_service.add_item("user1", 999, 1)


@patch("src.shopping.service.remove_item_from_cart")
def test_remove_item_success(mock_remove_item, cart_service, mock_session):
    # Setup
    user_id = "user1"
    product_id = 1
    quantity = 2

    mock_cart = MagicMock(spec=Cart)
    mock_product = MagicMock(spec=Product)

    cart_service.cart_repo.get_by_user_id_with_lock.return_value = mock_cart
    cart_service.product_repo.get_by_id_with_lock.return_value = mock_product

    # Act
    cart_service.remove_item(user_id, product_id, quantity)

    # Assert
    mock_remove_item.assert_called_once_with(mock_cart, mock_product, quantity)
    mock_session.commit.assert_called_once()


def test_remove_item_cart_not_found_raises_error(cart_service):
    # Setup
    cart_service.cart_repo.get_by_user_id_with_lock.return_value = None

    # Act & Assert
    with pytest.raises(CartNotFound):
        cart_service.remove_item("user1", 1, 1)
