from datetime import date

from app.engine.metrics.ticket import compute_average_ticket
from app.engine.metrics.types import SalesRecord


def _record(order_id: str, total_price: float) -> SalesRecord:
    return SalesRecord(
        order_id=order_id,
        order_date=date(2026, 7, 1),
        product_id=None,
        product_name="Produto A",
        sku=None,
        category=None,
        customer_id=None,
        quantity=1,
        unit_price=total_price,
        total_price=total_price,
        unit_cost=None,
    )


def test_average_ticket_groups_by_order():
    current = [_record("1", 50), _record("1", 50), _record("2", 100)]
    previous = [_record("3", 100)]

    result = compute_average_ticket(current, previous)

    assert result.average_current == 100.0
    assert result.average_previous == 100.0
    assert result.variation_pct == 0.0


def test_average_ticket_no_orders():
    result = compute_average_ticket([], [])

    assert result.average_current is None
    assert result.variation_pct is None
