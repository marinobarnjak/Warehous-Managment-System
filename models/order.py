from database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import datetime
from sqlalchemy import DateTime, func, Numeric, ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from models.supplier import Supplier
    from models.order_item import OrderItem

class Order(Base):
    __tablename__ = "orders"

    id : Mapped[int] = mapped_column(primary_key=True)
    status : Mapped[str] = mapped_column(nullable=False, server_default="pending")
    total_price : Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False, server_default="0")
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    supplier : Mapped["Supplier"] = relationship(back_populates="orders")
    supplier_id : Mapped[int] = mapped_column(ForeignKey("suppliers.id"))
    items : Mapped[list["OrderItem"]] = relationship(back_populates="order")

