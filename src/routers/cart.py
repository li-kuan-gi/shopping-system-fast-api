from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Product, CartItem
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

    # Check product stock with row-level lock
    product = (
        db.query(Product)
        .filter(Product.id == operation.product_id)
        .with_for_update()
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < operation.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    # Decrease product stock
    product.stock -= operation.quantity

    # Check if item exists in cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id, CartItem.product_id == operation.product_id
        )
        .first()
    )

    if cart_item:
        # Update existing item
        cart_item.quantity += operation.quantity
    else:
        # Insert new item
        cart_item = CartItem(
            user_id=user_id,
            product_id=operation.product_id,
            quantity=operation.quantity,
        )
        db.add(cart_item)

    # Commit the transaction
    db.commit()

    return {"status": "success", "message": "Item added to cart"}


@router.post("/remove-item", status_code=status.HTTP_200_OK)
def remove_item_from_cart(
    operation: CartItemOperation,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    user_id = user.id

    # Lock Product first (Acts as a gatekeeper for this product)
    product = (
        db.query(Product)
        .filter(Product.id == operation.product_id)
        .with_for_update()
        .first()
    )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id, CartItem.product_id == operation.product_id
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    # Calculate new quantity
    new_quantity: int = cart_item.quantity - operation.quantity

    if product:
        product.stock += operation.quantity

    if new_quantity <= 0:
        # Delete item
        db.delete(cart_item)
        db.commit()
        return {"status": "success", "message": "Item removed from cart"}
    else:
        # Update quantity
        cart_item.quantity = new_quantity
        db.commit()
        return {"status": "success", "message": "Item quantity decreased"}
