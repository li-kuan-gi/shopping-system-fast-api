from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import ClassVar


# Category Schemas
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int = 0
    category_id: int | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    stock: int | None = None
    category_id: int | None = None


class Product(ProductBase):
    id: int
    created_at: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


# Cart Schemas
class CartItemOperation(BaseModel):
    product_id: int
    quantity: int = 1
