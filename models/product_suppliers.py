from database.base import Base
from sqlalchemy import Table, Column, Integer, ForeignKey

product_suppliers = Table(
    "product_suppliers",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
    Column("supplier_id", Integer, ForeignKey("suppliers.id"), primary_key=True)
)

