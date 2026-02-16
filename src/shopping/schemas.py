from pydantic import BaseModel


# Cart Schemas
class CartItemOperation(BaseModel):
    product_id: int
    quantity: int = 1
