from database.connection import engine
from sqlalchemy.orm import Session
from services.product_service import ProductService
from sqlalchemy.exc import IntegrityError
from services.inventory_services import InventoryService

with Session(engine) as session: 
    product_service = ProductService(session) 
   
    inventory_service = InventoryService(session, product_service)

    # inventory_service.receive_stock("MIS-001", 10)
    # session.commit()

    issue = InventoryService(session)

    issue.issue_stock("MIS-001", 0)
    session.commit()
