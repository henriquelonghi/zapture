from datetime import date

from app.engine.metrics.churned_customers import compute_churned_customers
from app.engine.metrics.types import SalesRecord


def _record(customer_id, order_date):
    return SalesRecord(
        order_id=f"{customer_id}-{order_date}",
        order_date=order_date,
        product_id=None,
        product_name="Produto A",
        sku=None,
        category=None,
        customer_id=customer_id,
        quantity=1,
        unit_price=10,
        total_price=10,
        unit_cost=None,
    )


def test_customer_with_regular_purchases_not_flagged():
    records = [
        _record("c1", date(2026, 1, 1)),
        _record("c1", date(2026, 2, 1)),
        _record("c1", date(2026, 3, 1)),
    ]

    result = compute_churned_customers(records, as_of=date(2026, 3, 15))

    assert result == []


def test_customer_overdue_vs_history_is_flagged():
    records = [
        _record("c1", date(2026, 1, 1)),
        _record("c1", date(2026, 1, 15)),
        _record("c1", date(2026, 1, 29)),
    ]

    result = compute_churned_customers(records, as_of=date(2026, 3, 1))

    assert len(result) == 1
    assert result[0].customer_id == "c1"


def test_customer_below_min_orders_ignored():
    records = [_record("c1", date(2026, 1, 1))]

    result = compute_churned_customers(records, as_of=date(2026, 6, 1))

    assert result == []
