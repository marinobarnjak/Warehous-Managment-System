from database.base import Base
from sqlalchemy.orm import Mapped, mapped_column

class Product(Base):
    __tablename__ = "products"
    id : Mapped[int] = mapped_column(primary_key=True)
    name : Mapped[str] = mapped_column(nullable=False)
    sku : Mapped[str] = mapped_column(nullable=False, unique=True)