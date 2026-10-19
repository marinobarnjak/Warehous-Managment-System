from dotenv import load_dotenv
import os
from sqlalchemy import URL, create_engine, text


load_dotenv()
db_server = os.getenv("DB_SERVER")
db_port = int(os.getenv("DB_PORT"))
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

url_object = URL.create(
    "postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_server,
    port=db_port,
    database=db_name
)

engine = create_engine(url_object)

with engine.connect() as connection:
    connection
