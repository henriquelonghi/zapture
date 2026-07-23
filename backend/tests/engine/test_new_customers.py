from datetime import date

from app.engine.metrics.new_customers import compute_new_vs_returning
from app.engine.metrics.types import SalesRecord


def _record(order_id: str, order_date: date, customer_id: str, total_price: float = 100) -> SalesRecord:
    return SalesRecord(
        order_id=order_id,
        order_date=order_date,
        product_id=None,
        product_name="Produto A",
        sku=None,
        category=None,
        customer_id=customer_id,
        quantity=1,
        unit_price=total_price,
        total_price=total_price,
        unit_cost=None,
    )


def test_new_vs_returning_customers():
    period_start = date(2026, 7, 1)
    # cliente "antigo" comprou antes do período e de novo dentro dele
    returning_first = _record("1", date(2026, 6, 1), "returning-customer", total_price=50)
    returning_current = _record("2", date(2026, 7, 5), "returning-customer", total_price=80)
    # cliente "novo" só aparece pela primeira vez dentro do período
    new_current = _record("3", date(2026, 7, 10), "new-customer", total_price=120)

    full_history = [returning_first, returning_current, new_current]
    current = [returning_current, new_current]

    result = compute_new_vs_returning(current, full_history, period_start)

    assert result.new_customers_count == 1
    assert result.returning_customers_count == 1
    assert result.new_customers_revenue == 120
    assert result.returning_customers_revenue == 80


def test_new_vs_returning_ignores_records_without_customer():
    period_start = date(2026, 7, 1)
    anonymous = SalesRecord(
        order_id="1",
        order_date=date(2026, 7, 5),
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

    result = compute_new_vs_returning([anonymous], [anonymous], period_start)

    assert result.new_customers_count == 0
    assert result.returning_customers_count == 0
