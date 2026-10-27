from database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from decimal import Decimal
from sqlalchemy import Numeric
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.stock_movement import StockMovement
    from models.supplier import Supplier

class Product(Base):
    __tablename__ = "products"

    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=False)
    sku : Mapped[str] = mapped_column(nullable=False, unique=True)
    price : Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False, server_default="0")
    quantity : Mapped[int] = mapped_column(nullable=False, server_default="0")
    min_stock : Mapped[int] = mapped_column(nullable=False, server_default="0")
    stock_movement : Mapped[list["StockMovement"]] = relationship(back_populates="product")
    suppliers : Mapped[list["Supplier"]] = relationship(secondary="product_suppliers", back_populates="products")
