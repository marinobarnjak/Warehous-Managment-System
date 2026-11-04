from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.product_suppliers import product_suppliers
from services.product_service import ProductService
from services.supplier_service import SupplierService


@pytest.fixture
def supplier_service(db_session: Session):
    return SupplierService(db_session)


def test_create_supplier(supplier_service, db_session: Session):
    supplier = supplier_service.create_supplier(
        "Test Supplier",
        "test@supplier.com",
        "+385991234567"
    )
    db_session.flush()

    assert supplier.id is not None
    assert supplier.name == "Test Supplier"
    assert supplier.email == "test@supplier.com"
    assert supplier.phone == "+385991234567"


def test_create_supplier_without_contact(supplier_service, db_session: Session):
    supplier = supplier_service.create_supplier("Supplier Without Contact")
    db_session.flush()

    assert supplier.name == "Supplier Without Contact"
    assert supplier.email is None
    assert supplier.phone is None


def test_get_supplier(supplier_service, db_session: Session):
    created = supplier_service.create_supplier("Test Supplier")
    db_session.flush()

    supplier = supplier_service.get_supplier(created.id)

    assert supplier is not None
    assert supplier.id == created.id
    assert supplier.name == "Test Supplier"


def test_get_supplier_not_found(supplier_service):
    assert supplier_service.get_supplier(-1) is None


def test_get_all_suppliers(supplier_service, db_session: Session):
    supplier_service.create_supplier("Supplier A")
    supplier_service.create_supplier("Supplier B")
    db_session.flush()

    suppliers = supplier_service.get_all_suppliers()
    names = {supplier.name for supplier in suppliers}

    assert "Supplier A" in names
    assert "Supplier B" in names


def test_add_product_to_supplier(supplier_service, db_session: Session):
    product_service = ProductService(db_session)

    supplier = supplier_service.create_supplier("Supplier A")
    product = product_service.create_product(
        "Test Laptop", "SUP-LAPTOP-001",
        Decimal("999.90"), 5
    )
    db_session.flush()

    supplier_service.add_product_to_supplier(supplier.id, product.sku)
    db_session.flush()
    db_session.expire_all()

    saved_supplier = supplier_service.get_supplier(supplier.id)

    assert saved_supplier is not None
    assert product.sku in {p.sku for p in saved_supplier.products}


def test_supplier_multiple_products(supplier_service, db_session: Session):
    product_service = ProductService(db_session)

    supplier = supplier_service.create_supplier("Supplier A")
    product_service.create_product(
        "Laptop", "SUP-LAPTOP-002",
        Decimal("999.90"), 5
    )
    product_service.create_product(
        "Monitor", "SUP-MONITOR-001",
        Decimal("199.90"), 3
    )
    db_session.flush()

    supplier_service.add_product_to_supplier(supplier.id, "SUP-LAPTOP-002")
    supplier_service.add_product_to_supplier(supplier.id, "SUP-MONITOR-001")
    db_session.flush()

    skus = {product.sku for product in supplier.products}

    assert skus == {"SUP-LAPTOP-002", "SUP-MONITOR-001"}


def test_product_multiple_suppliers(supplier_service, db_session: Session):
    product_service = ProductService(db_session)

    supplier_a = supplier_service.create_supplier("Supplier A")
    supplier_b = supplier_service.create_supplier("Supplier B")
    product = product_service.create_product(
        "Laptop", "SUP-SHARED-001",
        Decimal("500.00"), 2
    )
    db_session.flush()

    supplier_service.add_product_to_supplier(supplier_a.id, product.sku)
    supplier_service.add_product_to_supplier(supplier_b.id, product.sku)
    db_session.flush()
    db_session.expire_all()

    supplier_ids = {supplier.id for supplier in product.suppliers}

    assert supplier_ids == {supplier_a.id, supplier_b.id}


def test_duplicate_supplier_product_link(supplier_service, db_session: Session):
    product_service = ProductService(db_session)

    supplier = supplier_service.create_supplier("Supplier A")
    product = product_service.create_product(
        "Laptop", "SUP-DUPLICATE-001",
        Decimal("500.00"), 2
    )
    db_session.flush()

    supplier_service.add_product_to_supplier(supplier.id, product.sku)
    supplier_service.add_product_to_supplier(supplier.id, product.sku)
    db_session.flush()

    rows = db_session.execute(
        select(product_suppliers).where(
            product_suppliers.c.supplier_id == supplier.id,
            product_suppliers.c.product_id == product.id
        )
    ).all()

    assert len(rows) == 1


def test_add_nonexistent_supplier(supplier_service, db_session: Session):
    product_service = ProductService(db_session)

    product_service.create_product(
        "Laptop", "SUP-NO-SUPPLIER",
        Decimal("500.00"), 2
    )
    db_session.flush()

    with pytest.raises(ValueError):
        supplier_service.add_product_to_supplier(-1, "SUP-NO-SUPPLIER")


def test_add_nonexistent_product(supplier_service, db_session: Session):
    supplier = supplier_service.create_supplier("Supplier A")
    db_session.flush()

    with pytest.raises(ValueError):
        supplier_service.add_product_to_supplier(
            supplier.id, "NONEXISTENT-SKU"
        )
