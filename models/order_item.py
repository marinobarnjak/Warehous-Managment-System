from database.base import Base
from sqlalchemy import Numeric,ForeignKey
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from models.product import Product
    from models.order import Order

class OrderItem(Base):
    __tablename__ = "order_items"

    id : Mapped[int] = mapped_column(primary_key=True)
    order_id : Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity : Mapped[int] = mapped_column(nullable=False)
    unit_price : Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    order : Mapped["Order"] = relationship(back_populates="items")
    product : Mapped["Product"] = relationship(back_populates="order_items")
