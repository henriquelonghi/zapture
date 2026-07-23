from datetime import date

from app.engine.metrics.types import SalesRecord
from app.engine.metrics.volume import compute_order_volume


def _record(order_id: str) -> SalesRecord:
    return SalesRecord(
        order_id=order_id,
        order_date=date(2026, 7, 1),
        product_id=None,
        product_name="Produto A",
        sku=None,
        category=None,
        customer_id=None,
        quantity=1,
        unit_price=10,
        total_price=10,
        unit_cost=None,
    )


def test_order_volume_variation():
    current = [_record("1"), _record("1"), _record("2")]
    previous = [_record("3")]

    result = compute_order_volume(current, previous)

    assert result.orders_current == 2
    assert result.orders_previous == 1
    assert result.variation_pct == 100.0
