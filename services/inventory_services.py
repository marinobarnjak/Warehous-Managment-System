from sqlalchemy import select
from sqlalchemy.orm import Session
from models.product import Product
from services.product_service import ProductService
from models.stock_movement import StockMovement

class InventoryService():

    def __init__(self, session: Session, product: ProductService) -> None:
        self.session = session
        self.product_service = product

    def receive_stock(self, sku: str, quantity: int) -> StockMovement:

        if quantity < 1:
            raise ValueError("Quantity must be greater than zero")

        product = self.product_service.get_product(sku)

        if not product:
            raise ValueError("Product with given SKU does not exist")
        
        product.quantity += quantity

        stock_movement = StockMovement()
        stock_movement.movement_type = "IN" 
        stock_movement.quantity = quantity
        stock_movement.product = product

        self.session.add(stock_movement)

        return stock_movement

    def issue_stock(self, sku: str, quantity: int) -> StockMovement:

        if quantity < 1:
            raise ValueError("Quantity must be greater than zero")

        product = self.product_service.get_product(sku)

        if not product:
            raise ValueError("Product with given SKU does not exist")

        if quantity > product.quantity:
            raise ValueError("Insufficient stock")

        product.quantity -= quantity

        stock_movement = StockMovement()
        stock_movement.movement_type = "OUT" 
        stock_movement.quantity = quantity
        stock_movement.product = product
        
        self.session.add(stock_movement)
        
        return stock_movement

    def get_stock(self, sku: str) -> int:
        product = self.product_service.get_product(sku)
        
        if not product:
            raise ValueError("Product with given SKU does not exist")

        return product.quantity

    def is_low_stock(self, sku: str) -> bool:
        product = self.product_service.get_product(sku)

        if not product:
            raise ValueError("Product with given SKU does not exist")

        return product.quantity < product.min_stock

    def get_low_stock_products(self) -> list[Product]:
        stmt = select(Product).where(Product.quantity < Product.min_stock)

        return self.session.scalars(stmt).all()
