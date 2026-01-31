from fastapi import APIRouter, HTTPException, status, Depends
from database import supabase
from schemas import Product, ProductCreate, ProductUpdate
from dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    _user: dict = Depends(  # pyright: ignore[reportCallInDefaultInitializer, reportMissingTypeArgument, reportUnknownParameterType]
        get_current_user
    ),
):
    product_data = product.model_dump(exclude_unset=True)
    response = supabase.table("products").insert(product_data).execute()
    return response.data[0]


@router.patch("/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    product: ProductUpdate,
    _user: dict = Depends(  # pyright: ignore[reportCallInDefaultInitializer, reportMissingTypeArgument, reportUnknownParameterType]
        get_current_user
    ),
):
    product_data = product.model_dump(exclude_unset=True)
    response = (
        supabase.table("products").update(product_data).eq("id", product_id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return response.data[0]


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    _user: dict = Depends(  # pyright: ignore[reportCallInDefaultInitializer, reportMissingTypeArgument, reportUnknownParameterType]
        get_current_user
    ),
):
    _ = supabase.table("products").delete().eq("id", product_id).execute()
    return None
