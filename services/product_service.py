from sqlalchemy.orm import Session
from models.product import Product
from sqlalchemy import select


class ProductService():

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_product(self, sku: str) -> Product | None: 
        stmt = select(Product).where(Product.sku == sku)

        return self.session.scalar(stmt)

    def create_product(self, name: str, sku: str) -> Product:
        product = Product()
        product.name = name
        product.sku = sku

        self.session.add(product)
        return product

    def get_all_products(self) -> list[Product]:
        stmt = select(Product)

        return self.session.scalars(stmt).all()
        
        