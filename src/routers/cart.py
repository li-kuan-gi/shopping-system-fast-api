from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.database import get_db
from src.models import Product, Cart
from src.schemas import CartItemOperation
from src.dependencies import get_current_user, User

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add-item", status_code=status.HTTP_200_OK)
def add_item_to_cart(
    operation: CartItemOperation,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user_id: str = user.id

    # 1. Atomic Cart Fetch/Create using ON CONFLICT
    stmt = (
        pg_insert(Cart)
        .values(user_id=user_id)
        .on_conflict_do_nothing(index_elements=["user_id"])
    )
    db.execute(stmt)

    # Lock Cart for update
    cart = db.query(Cart).filter(Cart.user_id == user_id).with_for_update().one()

    # 2. Lock Product first (to ensure stock consistency)
    product = (
        db.query(Product)
        .filter(Product.id == operation.product_id)
        .with_for_update()
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # 3. Use aggregate logic
        cart.add_item(product, operation.quantity)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "success", "message": "Item added to cart"}


@router.post("/remove-item", status_code=status.HTTP_200_OK)
def remove_item_from_cart(
    operation: CartItemOperation,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user_id = user.id

    # 1. Fetch and Lock Cart
    cart = db.query(Cart).filter(Cart.user_id == user_id).with_for_update().first()

    if not cart:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # 2. Lock Product
    product = (
        db.query(Product)
        .filter(Product.id == operation.product_id)
        .with_for_update()
        .first()
    )

    # Logic: Even if product is missing from DB (shouldn't happen with FKs),
    # we still need to handle it if we want to remove the item.
    # But usually, it's safer to just proceed if cart has it.
    if not product:
        # In a real system, we might still want to allow removal even if product is gone,
        # but here product.stock needs to be updated.
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        # 3. Use aggregate logic
        cart.remove_item(product, operation.quantity)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "success", "message": "Item removed from cart"}
