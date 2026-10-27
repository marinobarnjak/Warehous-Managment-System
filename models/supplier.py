from database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.product import Product

class Supplier(Base):
    __tablename__ = "suppliers"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=False)
    email : Mapped[str | None] = mapped_column(nullable=True)
    phone : Mapped[str | None] = mapped_column(nullable=True)
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    products : Mapped[list["Product"]] = relationship(secondary="product_suppliers", back_populates="suppliers")
