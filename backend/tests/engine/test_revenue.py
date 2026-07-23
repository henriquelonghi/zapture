from datetime import date

from app.engine.metrics.revenue import compute_revenue
from app.engine.metrics.types import SalesRecord


def _record(total_price: float, order_id: str = "1") -> SalesRecord:
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


def test_revenue_variation_positive():
    current = [_record(100), _record(50)]
    previous = [_record(100)]

    result = compute_revenue(current, previous)

    assert result.total_current == 150
    assert result.total_previous == 100
    assert result.variation_pct == 50.0


def test_revenue_variation_no_previous_data():
    result = compute_revenue([_record(100)], [])

    assert result.variation_pct is None
