from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    """Product model with only fields used in cart operations."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    stock = Column(Integer, nullable=False)

    # Relationship to cart items
    cart_items = relationship("CartItem", back_populates="product")


class CartItem(Base):
    """Cart item model linking users to products."""

    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relationship to product
    product = relationship("Product", back_populates="cart_items")
