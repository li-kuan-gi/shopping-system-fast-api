from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    Table,
    MetaData,
)
from sqlalchemy.orm import registry, relationship

# Define metadata and registry
metadata = MetaData()
mapper_registry = registry()


# Define Tables
products_table = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("stock", Integer, nullable=False),
)

carts_table = Table(
    "carts",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", String, unique=True, index=True, nullable=False),
)

cart_items_table = Table(
    "cart_items",
    metadata,
    Column("id", Integer, primary_key=True, index=True, autoincrement=True),
    Column("cart_id", Integer, ForeignKey("carts.id"), nullable=False),
    Column("product_id", Integer, ForeignKey("products.id"), nullable=False),
    Column("quantity", Integer, nullable=False),
    UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
)


from src.domain.models import Product, Cart, CartItem

# Map Classes to Tables
_ = mapper_registry.map_imperatively(
    Product,
    products_table,
)

_ = mapper_registry.map_imperatively(
    CartItem,
    cart_items_table,
    properties={
        "product": relationship(Product),
    },
)

_ = mapper_registry.map_imperatively(
    Cart,
    carts_table,
    properties={"items": relationship(CartItem, cascade="all, delete-orphan")},
)
