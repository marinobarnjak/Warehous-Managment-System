from sqlalchemy.orm import Session
from models.product import Product
from sqlalchemy import select
from decimal import Decimal

class ProductService():

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_product(self, sku: str) -> Product | None: 
        stmt = select(Product).where(Product.sku == sku)

        return self.session.scalar(stmt)

    def create_product(self, name: str, sku: str, price: Decimal, min_stock: int = 0) -> Product:

            name = name.strip()
            sku = sku.strip()
            if not name:
                raise ValueError("Name cannot be empty")
            if not sku: 
                raise ValueError("SKU cannot be empty")
            if price <= 0: 
                raise ValueError("Price must be greater than zero")
            if min_stock < 0:
                raise ValueError("Minimal stock cannot be a negative number")

            product = Product()
            product.name = name
            product.sku = sku
            product.price = price
            product.quntity = 0
            product.min_stock = min_stock
            
            self.session.add(product)
            return product

    def get_all_products(self) -> list[Product]:
        stmt = select(Product)

        return self.session.scalars(stmt).all()
        
    def update_product(self, sku: str, new_name: str) -> Product | None:
        product = self.get_product(sku)

        if product:
            product.name = new_name
            return product
        
        else:
            return None

    def delete_product(self, sku: str) -> bool:
        product = self.get_product(sku)

        if not product:
            return False

        self.session.delete(product)
        return True

