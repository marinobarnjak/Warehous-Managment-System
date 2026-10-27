from database.connection import engine
from sqlalchemy.orm import Session
from services.product_service import ProductService
from sqlalchemy.exc import IntegrityError
from services.inventory_services import InventoryService
from services.supplier_service import SupplierService

with Session(engine) as session: 
    product_service = ProductService(session)    
    inventory_service = InventoryService(session, product_service)
    supplier_service = SupplierService(session)

    supplier = supplier_service.add_product_to_supplier(1,"MIS-001")
    # session.commit()

    for product in supplier.products:
        print(f"Supplier: {supplier.name}\nProducts: {product.name}")



