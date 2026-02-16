from src.shopping.repository import ProductRepository
from src.shopping.domain import Product


def test_product_repo_get_by_id(db_session):
    repo = ProductRepository(db_session)
    product = Product(id=1, stock=10)
    db_session.add(product)
    db_session.commit()

    fetched = repo.get_by_id(1)
    assert fetched.id == 1
    assert fetched.stock == 10


def test_product_repo_get_by_id_with_lock(db_session):
    repo = ProductRepository(db_session)
    product = Product(id=1, stock=10)
    db_session.add(product)
    db_session.commit()

    # This just tests it returns the product, row-level locking behavior
    # is hard to verify in a single-threaded test but we verify the query runs.
    fetched = repo.get_by_id_with_lock(1)
    assert fetched.id == 1
    assert fetched.stock == 10


def test_product_repo_returns_none_if_not_found(db_session):
    repo = ProductRepository(db_session)
    assert repo.get_by_id(999) is None
