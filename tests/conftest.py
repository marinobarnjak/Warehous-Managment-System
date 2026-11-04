from dotenv import load_dotenv
import os
from sqlalchemy import URL, create_engine, text
from pathlib import Path
import pytest
from database.base import Base
import models
from sqlalchemy.orm import Session

path = Path(__file__).resolve().parent.parent / ".env.test"

if not path.exists():
    raise RuntimeError("Enviroment file for test database does not exist") 

load_dotenv(dotenv_path=path, override=True)
db_server = os.getenv("DB_SERVER")
db_port = int(os.getenv("DB_PORT"))
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

if db_name != "wms_test":
    raise RuntimeError("Database name is not 'wms_test'")

url_object = URL.create(
    "postgresql+psycopg",
    username=db_user,
    password=db_password,
    host=db_server,
    port=db_port,
    database=db_name
)

test_engine = create_engine(url_object)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    with test_engine.connect() as connection:
        stmt = text("SELECT current_database();")

        if connection.scalar(stmt) != "wms_test":
            raise RuntimeError("Current database is not 'wms_test'")
        
    Base.metadata.create_all(test_engine)

@pytest.fixture(scope="function")
def db_session(setup_database):
    connection = test_engine.connect()
    transaction = connection.begin()
    try:
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session

    finally:
        transaction.rollback()
        connection.close()

    




