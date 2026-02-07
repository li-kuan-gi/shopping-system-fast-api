from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from src.database import supabase
from src.schemas import CartItemOperation
from src.dependencies import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])


@router.post("/add-item", status_code=status.HTTP_200_OK)
def add_item_to_cart(
    operation: CartItemOperation,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    user_id: str | None = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Check if item exists in cart
    response = (
        supabase.table("cart_items")
        .select("quantity")
        .eq("user_id", user_id)
        .eq("product_id", operation.product_id)
        .execute()
    )

    if response.data:
        # Update existing item
        new_quantity: int = response.data[0]["quantity"] + operation.quantity
        _ = (
            supabase.table("cart_items")
            .update({"quantity": new_quantity})
            .eq("user_id", user_id)
            .eq("product_id", operation.product_id)
            .execute()
        )
    else:
        # Insert new item
        _ = (
            supabase.table("cart_items")
            .insert(
                {
                    "user_id": user_id,
                    "product_id": operation.product_id,
                    "quantity": operation.quantity,
                }
            )
            .execute()
        )

    return {"status": "success", "message": "Item added to cart"}


@router.post("/remove-item", status_code=status.HTTP_200_OK)
def remove_item_from_cart(
    operation: CartItemOperation,
    user: Annotated[dict[str, object], Depends(get_current_user)],
):
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Check if item exists in cart
    response = (
        supabase.table("cart_items")
        .select("quantity")
        .eq("user_id", user_id)
        .eq("product_id", operation.product_id)
        .execute()
    )

    if not response.data:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    current_quantity: int = response.data[0]["quantity"]
    new_quantity: int = current_quantity - operation.quantity

    if new_quantity <= 0:
        # Delete item
        _ = (
            supabase.table("cart_items")
            .delete()
            .eq("user_id", user_id)
            .eq("product_id", operation.product_id)
            .execute()
        )
        return {"status": "success", "message": "Item removed from cart"}
    else:
        # Update quantity
        _ = (
            supabase.table("cart_items")
            .update({"quantity": new_quantity})
            .eq("user_id", user_id)
            .eq("product_id", operation.product_id)
            .execute()
        )
        return {"status": "success", "message": "Item quantity decreased"}
