from database.connection import engine
from sqlalchemy.orm import Session
from services.product_service import ProductService

with Session(engine) as session: 
    product_service = ProductService(session) 

    # get_product = product_service.get_product("MIS-001") 

    # if get_product:
    #     print(f"Product found!\nName: {get_product.name}\nSKU: {get_product.sku}")
    # else:
    #     print("Product not found")

    # create = product_service.create_product("Razer Viper V3", "MIS-002")
    # session.commit()

    # print(f"Name: {create.name}\nSKU: {create.sku}")

    all_products = product_service.get_all_products()
    
    for obj in all_products:
        print(f"ID: {obj.id}\nName: {obj.name}\nSKU: {obj.sku}")