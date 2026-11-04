from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.product import Product
from models.stock_movement import StockMovement
from services.product_service import ProductService
from services.inventory_services import InventoryService


@pytest.fixture
def inventory(db_session: Session):
    product_service = ProductService(db_session)
    inventory_service = InventoryService(db_session, product_service)

    product_service.create_product(
        "Test Laptop", "INV-LAPTOP-001",
        Decimal("999.90"), 5
    )
    db_session.flush()

    return inventory_service


def test_receive_stock(inventory, db_session: Session):
    movement = inventory.receive_stock("INV-LAPTOP-001", 10)
    db_session.flush()

    assert inventory.get_stock("INV-LAPTOP-001") == 10
    assert movement.movement_type == "IN"
    assert movement.quantity == 10
    assert movement.product.sku == "INV-LAPTOP-001"


def test_issue_stock(inventory, db_session: Session):
    inventory.receive_stock("INV-LAPTOP-001", 10)
    movement = inventory.issue_stock("INV-LAPTOP-001", 4)
    db_session.flush()

    assert inventory.get_stock("INV-LAPTOP-001") == 6
    assert movement.movement_type == "OUT"
    assert movement.quantity == 4


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_receive_invalid_quantity(inventory, quantity):
    with pytest.raises(ValueError):
        inventory.receive_stock("INV-LAPTOP-001", quantity)


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_issue_invalid_quantity(inventory, quantity):
    inventory.receive_stock("INV-LAPTOP-001", 10)

    with pytest.raises(ValueError):
        inventory.issue_stock("INV-LAPTOP-001", quantity)


def test_issue_insufficient_stock(inventory):
    inventory.receive_stock("INV-LAPTOP-001", 5)

    with pytest.raises(ValueError):
        inventory.issue_stock("INV-LAPTOP-001", 10)

    assert inventory.get_stock("INV-LAPTOP-001") == 5


def test_issue_all_stock(inventory):
    inventory.receive_stock("INV-LAPTOP-001", 10)
    inventory.issue_stock("INV-LAPTOP-001", 10)

    assert inventory.get_stock("INV-LAPTOP-001") == 0


def test_get_stock(inventory):
    assert inventory.get_stock("INV-LAPTOP-001") == 0

    inventory.receive_stock("INV-LAPTOP-001", 15)

    assert inventory.get_stock("INV-LAPTOP-001") == 15


@pytest.mark.parametrize(
    "quantity, expected",
    [
        (0, True),
        (4, True),
        (5, False),
        (6, False),
    ],
)
def test_is_low_stock(inventory, quantity, expected):
    if quantity > 0:
        inventory.receive_stock("INV-LAPTOP-001", quantity)

    assert inventory.is_low_stock("INV-LAPTOP-001") is expected


def test_get_low_stock_products(inventory, db_session: Session):
    product_service = ProductService(db_session)

    product_service.create_product(
        "Test Monitor", "INV-MONITOR-001",
        Decimal("199.90"), 3
    )
    db_session.flush()

    inventory.receive_stock("INV-LAPTOP-001", 10)

    products = inventory.get_low_stock_products()
    skus = {product.sku for product in products}

    assert "INV-MONITOR-001" in skus
    assert "INV-LAPTOP-001" not in skus


def test_stock_movement_history(inventory, db_session: Session):
    inventory.receive_stock("INV-LAPTOP-001", 10)
    inventory.issue_stock("INV-LAPTOP-001", 3)
    db_session.flush()

    movements = db_session.scalars(
        select(StockMovement)
        .join(Product)
        .where(Product.sku == "INV-LAPTOP-001")
        .order_by(StockMovement.id)
    ).all()

    assert len(movements) == 2
    assert movements[0].movement_type == "IN"
    assert movements[0].quantity == 10
    assert movements[1].movement_type == "OUT"
    assert movements[1].quantity == 3
    assert inventory.get_stock("INV-LAPTOP-001") == 7


@pytest.mark.parametrize(
    "method",
    ["receive_stock", "issue_stock"],
)
def test_nonexistent_product(inventory, method):
    operation = getattr(inventory, method)

    with pytest.raises(ValueError):
        operation("NONEXISTENT-SKU", 5)
