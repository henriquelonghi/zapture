from datetime import date

from app.engine.metrics.top_products import compute_bestseller, compute_highest_priced_sale
from app.engine.metrics.types import SalesRecord


def _record(order_id, product_name, quantity, unit_price, sku=None, product_id=None):
    return SalesRecord(
        order_id=order_id,
        order_date=date(2026, 7, 10),
        product_id=product_id,
        product_name=product_name,
        sku=sku,
        category=None,
        customer_id=None,
        quantity=quantity,
        unit_price=unit_price,
        total_price=quantity * unit_price,
        unit_cost=None,
    )


def test_compute_bestseller_picks_highest_units_not_highest_revenue():
    records = [
        _record("P1", "Produto A", quantity=10, unit_price=5),
        _record("P2", "Produto B", quantity=2, unit_price=100),
    ]

    result = compute_bestseller(records)

    assert result is not None
    assert result.product_name == "Produto A"
    assert result.units_sold == 10
    assert result.revenue == 50


def test_compute_bestseller_groups_by_sku_across_orders():
    records = [
        _record("P1", "Produto A", quantity=3, unit_price=10, sku="SKU-A"),
        _record("P2", "Produto A", quantity=4, unit_price=10, sku="SKU-A"),
        _record("P3", "Produto B", quantity=5, unit_price=1, sku="SKU-B"),
    ]

    result = compute_bestseller(records)

    assert result is not None
    assert result.product_key == "SKU-A"
    assert result.units_sold == 7


def test_compute_bestseller_returns_none_for_empty_period():
    assert compute_bestseller([]) is None


def test_compute_highest_priced_sale_picks_max_unit_price():
    records = [
        _record("P1", "Produto Barato", quantity=10, unit_price=5),
        _record("P2", "Produto Caro", quantity=1, unit_price=999),
    ]

    result = compute_highest_priced_sale(records)

    assert result is not None
    assert result.product_name == "Produto Caro"
    assert result.unit_price == 999
    assert result.order_id == "P2"


def test_compute_highest_priced_sale_returns_none_for_empty_period():
    assert compute_highest_priced_sale([]) is None
