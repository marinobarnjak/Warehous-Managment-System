from database.connection import engine
from sqlalchemy.orm import Session
from services.product_service import ProductService
from sqlalchemy.exc import IntegrityError

with Session(engine) as session: 
    product_service = ProductService(session) 

    try:
        create = product_service.create_product(
            "Samsung Odyssey G5",
            "MON-001",
            "249.99",
            "3"
            )
        session.commit()
        print(f"Name: {create.name}\nSKU: {create.sku}")

    except ValueError as e:
        print(e)

    except IntegrityError:
        session.rollback()
        print("spremanje proizvoda nije uspjelo zbog ograničenja baze")

    get_product = product_service.get_product("MON-001") 
    if get_product:
        print(f"Product found!\nName: {get_product.name}\nSKU: {get_product.sku}")
    else:
        print("Product not found")
   
        