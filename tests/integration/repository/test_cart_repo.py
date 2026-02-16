from src.shopping.repository import CartRepository
from src.shopping.domain import Cart


def test_cart_repo_create_if_not_exists(db_session):
    repo = CartRepository(db_session)
    user_id = "test_user"

    repo.create_if_not_exists(user_id)
    db_session.commit()

    cart = db_session.query(Cart).filter(Cart.user_id == user_id).first()
    assert cart is not None
    assert cart.user_id == user_id

    # Try again, should not raise error (on conflict do nothing)
    repo.create_if_not_exists(user_id)
    db_session.commit()

    carts = db_session.query(Cart).filter(Cart.user_id == user_id).all()
    assert len(carts) == 1


def test_cart_repo_get_by_user_id_with_lock(db_session):
    repo = CartRepository(db_session)
    user_id = "test_user"
    cart = Cart(user_id=user_id)
    db_session.add(cart)
    db_session.commit()

    fetched = repo.get_by_user_id_with_lock(user_id)
    assert fetched is not None
    assert fetched.user_id == user_id


def test_cart_repo_returns_none_if_not_found(db_session):
    repo = CartRepository(db_session)
    assert repo.get_by_user_id_with_lock("none") is None
