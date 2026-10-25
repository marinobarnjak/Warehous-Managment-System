from database.base import Base
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from models.product import Product

class StockMovement(Base):
    __tablename__ = "stock_movements"
    
    id : Mapped[int] = mapped_column(primary_key=True)
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"))
    movement_type : Mapped[str] = mapped_column(nullable=False)
    quantity : Mapped[int] = mapped_column(nullable=False)
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    product : Mapped["Product"] = relationship(back_populates="stock_movement")