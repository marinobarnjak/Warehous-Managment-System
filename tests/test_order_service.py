from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from models.stock_movement import StockMovement
from services.product_service import ProductService
from services.supplier_service import SupplierService
from services.inventory_services import InventoryService
from services.order_service import OrderService


@pytest.fixture
def order_context(db_session: Session):
    product_service = ProductService(db_session)
    supplier_service = SupplierService(db_session)
    inventory_service = InventoryService(db_session, product_service)
    order_service = OrderService(db_session)

    supplier = supplier_service.create_supplier(
        "Test Supplier", None, None
    )

    laptop = product_service.create_product(
        "Laptop", "ORD-LAPTOP-001",
        Decimal("500.00"), 5
    )

    monitor = product_service.create_product(
        "Monitor", "ORD-MONITOR-001",
        Decimal("200.00"), 3
    )

    db_session.flush()

    supplier_service.add_product_to_supplier(supplier.id, laptop.sku)
    supplier_service.add_product_to_supplier(supplier.id, monitor.sku)
    db_session.flush()

    return {
        "supplier": supplier,
        "laptop": laptop,
        "monitor": monitor,
        "orders": order_service,
        "inventory": inventory_service,
    }


def test_create_order(order_context, db_session: Session):
    service = order_context["orders"]
    supplier = order_context["supplier"]

    order = service.create_order(supplier.id)
    db_session.flush()

    assert order.id is not None
    assert order.supplier_id == supplier.id
    assert order.status == "pending"
    assert order.total_price == Decimal("0.00")


def test_create_order_invalid_supplier(order_context):
    service = order_context["orders"]

    with pytest.raises(ValueError):
        service.create_order(-1)


def test_get_order(order_context, db_session: Session):
    service = order_context["orders"]

    created = service.create_order(order_context["supplier"].id)
    db_session.flush()

    found = service.get_order(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_order_not_found(order_context):
    assert order_context["orders"].get_order(-1) is None


def test_add_item(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    item = service.add_item(order.id, "ORD-LAPTOP-001", 3)
    db_session.flush()

    assert item.order_id == order.id
    assert item.product_id == order_context["laptop"].id
    assert item.quantity == 3
    assert item.unit_price == Decimal("500.00")
    assert order.total_price == Decimal("1500.00")


def test_multiple_items_total(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 2)
    service.add_item(order.id, "ORD-MONITOR-001", 3)
    db_session.flush()

    assert len(order.items) == 2
    assert order.total_price == Decimal("1600.00")


@pytest.mark.parametrize("quantity", [0, -1, -5])
def test_add_item_invalid_quantity(order_context, db_session, quantity):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    with pytest.raises(ValueError):
        service.add_item(order.id, "ORD-LAPTOP-001", quantity)


def test_add_item_unknown_product(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    with pytest.raises(ValueError):
        service.add_item(order.id, "UNKNOWN-SKU", 2)


def test_add_item_unrelated_supplier(order_context, db_session: Session):
    service = order_context["orders"]
    product_service = ProductService(db_session)

    product_service.create_product(
        "Keyboard", "ORD-KEYBOARD-001",
        Decimal("50.00"), 1
    )

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    with pytest.raises(ValueError):
        service.add_item(order.id, "ORD-KEYBOARD-001", 2)


def test_add_duplicate_item(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 2)
    db_session.flush()

    with pytest.raises(ValueError):
        service.add_item(order.id, "ORD-LAPTOP-001", 3)


def test_complete_order(order_context, db_session: Session):
    service = order_context["orders"]
    inventory = order_context["inventory"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 4)
    service.add_item(order.id, "ORD-MONITOR-001", 2)
    db_session.flush()

    completed = service.complete_order(order.id)
    db_session.flush()

    assert completed.status == "completed"
    assert inventory.get_stock("ORD-LAPTOP-001") == 4
    assert inventory.get_stock("ORD-MONITOR-001") == 2

    movements = db_session.scalars(
        select(StockMovement).where(
            StockMovement.product_id.in_([
                order_context["laptop"].id,
                order_context["monitor"].id,
            ])
        )
    ).all()

    assert len(movements) == 2
    assert all(m.movement_type == "IN" for m in movements)
    assert sum(m.quantity for m in movements) == 6


def test_complete_empty_order(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    with pytest.raises(ValueError):
        service.complete_order(order.id)

    assert order.status == "pending"


def test_complete_order_twice(order_context, db_session: Session):
    service = order_context["orders"]
    inventory = order_context["inventory"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 5)
    db_session.flush()

    service.complete_order(order.id)
    db_session.flush()

    with pytest.raises(ValueError):
        service.complete_order(order.id)

    assert inventory.get_stock("ORD-LAPTOP-001") == 5


def test_cancel_order(order_context, db_session: Session):
    service = order_context["orders"]
    inventory = order_context["inventory"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 3)
    db_session.flush()

    cancelled = service.cancel_order(order.id)
    db_session.flush()

    assert cancelled.status == "cancelled"
    assert inventory.get_stock("ORD-LAPTOP-001") == 0


def test_cancel_order_twice(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.cancel_order(order.id)

    with pytest.raises(ValueError):
        service.cancel_order(order.id)


def test_complete_cancelled_order(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 2)
    db_session.flush()

    service.cancel_order(order.id)

    with pytest.raises(ValueError):
        service.complete_order(order.id)


def test_cancel_completed_order(order_context, db_session: Session):
    service = order_context["orders"]

    order = service.create_order(order_context["supplier"].id)
    db_session.flush()

    service.add_item(order.id, "ORD-LAPTOP-001", 2)
    db_session.flush()

    service.complete_order(order.id)

    with pytest.raises(ValueError):
        service.cancel_order(order.id)

def test_complete_order_atomicity(db_session: Session):
    product_service = ProductService(db_session)
    supplier_service = SupplierService(db_session)
    order_service = OrderService(db_session)

    supplier = supplier_service.create_supplier("HgSpot", None, None)

    product_service.create_product(
        "Tipkovnica", "TIP-001", Decimal("29.99"), 5
    )
    product_service.create_product(
        "Mis", "MIS-001", Decimal("19.99"), 5
    )

    db_session.flush()

    supplier_service.add_product_to_supplier(supplier.id, "TIP-001")
    supplier_service.add_product_to_supplier(supplier.id, "MIS-001")

    order = order_service.create_order(supplier.id)
    db_session.flush()

    order_service.add_item(order.id, "TIP-001", 2)
    order_service.add_item(order.id, "MIS-001", 3)

    db_session.flush()

    orginal_receive = InventoryService.receive_stock
    counter = 0

    def fake_receive(self, sku, quantity):
        nonlocal counter 
        counter += 1

        if counter == 2: 
            raise RuntimeError("Simulated receiving failure")

        return orginal_receive(self, sku, quantity)

    with pytest.raises(RuntimeError):
        with db_session.begin_nested():
            with patch.object(InventoryService, "receive_stock", fake_receive):
                order_service.complete_order(order.id)

    assert counter == 2

    ord = order_service.get_order(order.id)
    assert ord.status == "pending"

    inventory_service = InventoryService(db_session, product_service)
    firstProduct = inventory_service.get_stock("TIP-001")
    secondProduct = inventory_service.get_stock("MIS-001")

    assert firstProduct == 0
    assert secondProduct == 0

    tip = product_service.get_product("TIP-001")
    mis = product_service.get_product("MIS-001")
    movements = db_session.scalars(
    select(StockMovement).where(
        StockMovement.product_id.in_([tip.id, mis.id])
        )
    ).all()

    assert len(movements) == 0
