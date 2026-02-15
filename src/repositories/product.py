import logging
from sqlalchemy.orm import Session
from src.domain.models import Product
from src.models import products_table

logger = logging.getLogger(__name__)


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
        logger.debug(f"Executing SELECT FOR UPDATE on products for id: {product_id}")
        return (
            self.session.query(Product)
            .filter(products_table.c.id == product_id)
            .with_for_update()
            .first()
        )
