from sqlalchemy.orm import Session
from src.models import Product, products_table


class ProductRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, product_id: int) -> Product | None:
        return (
            self.session.query(Product)
            .filter(products_table.c.id == product_id)
            .first()
        )

    def get_by_id_with_lock(self, product_id: int) -> Product | None:
        return (
            self.session.query(Product)
            .filter(products_table.c.id == product_id)
            .with_for_update()
            .first()
        )
