from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.models import Cart, carts_table


class CartRepository:
    session: Session

    def __init__(self, session: Session):
        self.session = session

    def get_by_user_id(self, user_id: str) -> Cart | None:
        return self.session.query(Cart).filter(carts_table.c.user_id == user_id).first()

    def get_by_user_id_with_lock(self, user_id: str) -> Cart | None:
        return (
            self.session.query(Cart)
            .filter(carts_table.c.user_id == user_id)
            .with_for_update()
            .first()
        )

    def create_if_not_exists(self, user_id: str) -> None:
        stmt = (
            pg_insert(Cart)
            .values(user_id=user_id)
            .on_conflict_do_nothing(index_elements=["user_id"])
        )
        _ = self.session.execute(stmt)
