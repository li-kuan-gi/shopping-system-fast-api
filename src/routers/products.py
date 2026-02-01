from fastapi import APIRouter, HTTPException, status
from database import supabase
from schemas import Product, ProductCreate, ProductUpdate
from dependencies import login_required

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=Product, status_code=status.HTTP_201_CREATED)
@login_required
def create_product(
    product: ProductCreate,
):
    product_data = product.model_dump(exclude_unset=True)
    response = supabase.table("products").insert(product_data).execute()
    return response.data[0]


@router.patch("/{product_id}", response_model=Product)
@login_required
def update_product(
    product_id: int,
    product: ProductUpdate,
):
    product_data = product.model_dump(exclude_unset=True)
    response = (
        supabase.table("products").update(product_data).eq("id", product_id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Product not found")
    return response.data[0]


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
@login_required
def delete_product(
    product_id: int,
):
    _ = supabase.table("products").delete().eq("id", product_id).execute()
    return None
