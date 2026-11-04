from decimal import Decimal
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from services.product_service import ProductService

def test_create_product(db_session: Session):
    service = ProductService(db_session)

    product = service.create_product(
        "Test Laptop", "TEST-LAPTOP-001",
        Decimal("999.90"), 5
    )
    db_session.flush()

    assert product.id is not None
    assert product.name == "Test Laptop"
    assert product.sku == "TEST-LAPTOP-001"
    assert product.price == Decimal("999.90")
    assert product.quantity == 0
    assert product.min_stock == 5


@pytest.mark.parametrize(
    "name, sku, price, min_stock",
    [
        ("", "TEST-001", Decimal("100.00"), 5),
        ("   ", "TEST-001", Decimal("100.00"), 5),
        ("Laptop", "", Decimal("100.00"), 5),
        ("Laptop", "   ", Decimal("100.00"), 5),
        ("Laptop", "TEST-001", Decimal("-50.00"), 5),
        ("Laptop", "TEST-001", Decimal("0.00"), 5),
        ("Laptop", "TEST-001", Decimal("100.00"), -1),
    ],
)
def test_create_product_invalid_params(
    db_session: Session, name, sku, price, min_stock
):
    service = ProductService(db_session)

    with pytest.raises(ValueError):
        service.create_product(name, sku, price, min_stock)


def test_get_product(db_session: Session):
    service = ProductService(db_session)

    service.create_product(
        "Test Monitor", "TEST-MONITOR-001",
        Decimal("199.99"), 3
    )
    db_session.flush()
    db_session.expire_all()

    product = service.get_product("TEST-MONITOR-001")

    assert product is not None
    assert product.name == "Test Monitor"
    assert product.price == Decimal("199.99")


def test_get_product_not_found(db_session: Session):
    service = ProductService(db_session)

    assert service.get_product("NONEXISTENT-001") is None


def test_get_all_products(db_session: Session):
    service = ProductService(db_session)

    service.create_product(
        "Laptop", "ALL-LAPTOP-001", Decimal("500.00"), 2
    )
    service.create_product(
        "Monitor", "ALL-MONITOR-001", Decimal("200.00"), 2
    )
    db_session.flush()

    products = service.get_all_products()
    skus = {product.sku for product in products}

    assert "ALL-LAPTOP-001" in skus
    assert "ALL-MONITOR-001" in skus


def test_update_product(db_session: Session):
    service = ProductService(db_session)

    service.create_product(
        "Old Laptop", "UPDATE-001",
        Decimal("999.90"), 5
    )
    db_session.flush()

    service.update_product("UPDATE-001", "New Laptop")
    db_session.flush()
    db_session.expire_all()

    product = service.get_product("UPDATE-001")

    assert product is not None
    assert product.name == "New Laptop"
    assert product.sku == "UPDATE-001"
    assert product.price == Decimal("999.90")


def test_delete_product(db_session: Session):
    service = ProductService(db_session)

    service.create_product(
        "Delete Laptop", "DELETE-001",
        Decimal("300.00"), 1
    )
    db_session.flush()

    service.delete_product("DELETE-001")
    db_session.flush()

    assert service.get_product("DELETE-001") is None


def test_duplicate_sku(db_session: Session):
    service = ProductService(db_session)

    service.create_product(
        "Laptop A", "DUPLICATE-001",
        Decimal("100.00"), 1
    )
    db_session.flush()

    with pytest.raises(IntegrityError):
        with db_session.begin_nested():
            service.create_product(
                "Laptop B", "DUPLICATE-001",
                Decimal("200.00"), 1
            )
            db_session.flush()

    original = service.get_product("DUPLICATE-001")

    assert original is not None
    assert original.name == "Laptop A"
