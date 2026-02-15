from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    """Product model with only fields used in cart operations."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    stock = Column(Integer, nullable=False)

    # Relationship to cart items
    cart_items = relationship("CartItem", back_populates="product")


class Cart(Base):
    """Cart aggregate root."""

    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)

    # Relationship to cart items
    items = relationship(
        "CartItem", back_populates="cart", cascade="all, delete-orphan"
    )

    def add_item(self, product: Product, quantity: int):
        """Add an item to the cart and decrease product stock."""
        if product.stock < quantity:
            raise ValueError("Insufficient stock")

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

        raise ValueError("Item not found in cart")


class CartItem(Base):
    """Cart item model linking carts to products."""

    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )
