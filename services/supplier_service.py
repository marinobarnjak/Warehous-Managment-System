from sqlalchemy.orm import Session
from models.supplier import Supplier
from sqlalchemy import select
from services.product_service import ProductService

class SupplierService():
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_supplier(self, id: int) -> Supplier:
        stmt = select(Supplier).where(Supplier.id == id)

        return self.session.scalar(stmt)

    def get_all_suppliers(self) -> list[Supplier]:
        stmt = select(Supplier)

        return self.session.scalars(stmt).all()

    def create_supplier(self, name: str, email: str | None, phone: str | None) -> Supplier | None:
        name = name.strip()

        if not name:
            raise ValueError("Name cannot be empty")

        supplier = Supplier()
        supplier.name = name

        if email:
            supplier.email = email.strip()  

        if phone: 
            supplier.phone = phone.strip()

        self.session.add(supplier)
        return supplier

    def add_product_to_supplier(self, supplier_id : int, sku: str) -> Supplier:

        supplier = self.get_supplier(supplier_id)
        product = ProductService(self.session)
        product = product.get_product(sku)

        if not supplier:
            raise ValueError("Supplier does not exist")
        if not product:
            raise ValueError("Product does not exist")

        if product not in supplier.products:
            supplier.products.append(product)

        return supplier
        