from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.shopping.service import CartService


def get_cart_service(db: Annotated[Session, Depends(get_db)]) -> CartService:
    return CartService(db)
