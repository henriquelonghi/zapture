from datetime import date

from app.engine.metrics.types import SalesRecord
from app.engine.metrics.units import compute_units_sold


def _record(quantity: float) -> SalesRecord:
    return SalesRecord(
        order_id="1",
        order_date=date(2026, 7, 1),
        product_id=None,
        product_name="Produto A",
        sku=None,
        category=None,
        customer_id=None,
        quantity=quantity,
        unit_price=10,
        total_price=10 * quantity,
        unit_cost=None,
    )


def test_units_sold_variation():
    current = [_record(2), _record(3)]
    previous = [_record(4)]

    result = compute_units_sold(current, previous)

    assert result.units_current == 5
    assert result.units_previous == 4
    assert result.variation_pct == 25.0


def test_units_sold_no_previous():
    result = compute_units_sold([_record(2)], [])

    assert result.units_current == 2
    assert result.units_previous == 0
    assert result.variation_pct is None
