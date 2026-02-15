import logging
from typing import Annotated
from fastapi import APIRouter, status, Depends, HTTPException
from src.schemas import CartItemOperation
from src.dependencies import get_current_user, User, get_cart_service
from src.services.cart import CartService
from src.domain.exceptions import InsufficientStock, ItemNotFoundInCart
from src.services.exceptions import CartNotFound, ProductNotFound

router = APIRouter(prefix="/cart", tags=["cart"])
logger = logging.getLogger(__name__)


@router.post("/add-item", status_code=status.HTTP_200_OK)
def add_item_to_cart(
    operation: CartItemOperation,
    user: Annotated[User, Depends(get_current_user)],
    cart_service: Annotated[CartService, Depends(get_cart_service)],
):
    logger.info(
        f"User {user.id} adding {operation.quantity} of product {operation.product_id} to cart"
    )
    try:
        cart_service.add_item(user.id, operation.product_id, operation.quantity)
        logger.info(
            f"Successfully added product {operation.product_id} to cart for user {user.id}"
        )
        return {"status": "success", "message": "Item added to cart"}
    except CartNotFound as e:
        logger.error(f"Cart not found for user {user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except ProductNotFound as e:
        logger.warning(f"Product {operation.product_id} not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InsufficientStock as e:
        logger.warning(
            f"Insufficient stock for product {operation.product_id} (requested {operation.quantity}): {e}"
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/remove-item", status_code=status.HTTP_200_OK)
def remove_item_from_cart(
    operation: CartItemOperation,
    user: Annotated[User, Depends(get_current_user)],
    cart_service: Annotated[CartService, Depends(get_cart_service)],
):
    logger.info(
        f"User {user.id} removing {operation.quantity} of product {operation.product_id} from cart"
    )
    try:
        cart_service.remove_item(user.id, operation.product_id, operation.quantity)
        logger.info(
            f"Successfully removed product {operation.product_id} from cart for user {user.id}"
        )
        return {"status": "success", "message": "Item removed from cart"}
    except (CartNotFound, ItemNotFoundInCart) as e:
        logger.warning(f"Item/Cart error for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ProductNotFound as e:
        logger.warning(f"Product {operation.product_id} not found: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InsufficientStock as e:
        logger.warning(f"Stock error during removal for user {user.id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
