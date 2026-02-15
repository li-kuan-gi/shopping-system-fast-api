import logging
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.domain.models import Cart
from src.models import carts_table

logger = logging.getLogger(__name__)


class CartRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_by_user_id_with_lock(self, user_id: str) -> Cart | None:
        logger.debug(f"Executing SELECT FOR UPDATE on carts for user_id: {user_id}")
        return (
            self.session.query(Cart)
            .filter(carts_table.c.user_id == user_id)
            .with_for_update()
            .first()
        )

    def create_if_not_exists(self, user_id: str) -> None:
        logger.debug(
            f"Executing ON CONFLICT DO NOTHING insert for cart (user_id: {user_id})"
        )
        stmt = (
            pg_insert(Cart)
            .values(user_id=user_id)
            .on_conflict_do_nothing(index_elements=["user_id"])
        )
        _ = self.session.execute(stmt)
