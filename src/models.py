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

from src.domain.exceptions import InsufficientStock, ItemNotFoundInCart

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


# Define Domain Classes
class Product:
    """Product domain model."""

    id: int
    stock: int

    def __init__(self, id: int, stock: int):
        self.id = id
        self.stock = stock


class CartItem:
    """Cart item domain model."""

    cart_id: int | None
    product_id: int | None
    quantity: int

    def __init__(
        self,
        cart_id: int | None = None,
        product_id: int | None = None,
        quantity: int = 0,
    ):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity


class Cart:
    """Cart aggregate root."""

    user_id: str
    items: list[CartItem]

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.items = []

    def add_item(self, product: Product, quantity: int):
        """Add an item to the cart and decrease product stock."""
        if product.stock < quantity:
            raise InsufficientStock()

        product.stock -= quantity

        # Update existing item or add new
        for item in self.items:
            if item.product_id == product.id:
                item.quantity += quantity
                return

        new_item = CartItem(product_id=product.id, quantity=quantity)
        self.items.append(new_item)

    def remove_item(self, product: Product, quantity: int):
        """Remove an item from the cart (or decrease quantity) and increase product stock."""
        for item in self.items:
            if item.product_id == product.id:
                # Increase stock (don't return more than what was in the cart)
                actual_return = min(item.quantity, quantity)
                product.stock += actual_return

                item.quantity -= quantity
                if item.quantity <= 0:
                    self.items.remove(item)
                return

        raise ItemNotFoundInCart()


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
