from database.connection import engine
from sqlalchemy.orm import Session
from services.product_service import ProductService
from sqlalchemy.exc import IntegrityError
from services.inventory_services import InventoryService
from services.supplier_service import SupplierService
from services.order_service import OrderService

with Session(engine) as session: 
    product_service = ProductService(session)    
    inventory_service = InventoryService(session, product_service)
    supplier_service = SupplierService(session)
    order_service = OrderService(session)


    order_service.complete_order(1)
    session.commit()