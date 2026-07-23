from datetime import date

from app.engine.metrics.margin import compute_aggregate_margin, compute_product_margins
from app.engine.metrics.types import SalesRecord


def _record(product_name, sku, unit_price, unit_cost, quantity=1):
    return SalesRecord(
        order_id="1",
        order_date=date(2026, 7, 1),
        product_id=None,
        product_name=product_name,
        sku=sku,
        category=None,
        customer_id=None,
        quantity=quantity,
        unit_price=unit_price,
        total_price=unit_price * quantity,
        unit_cost=unit_cost,
    )


def test_product_margin_with_known_cost():
    margins = compute_product_margins([_record("Produto A", "SKU1", 100, 60)])

    assert len(margins) == 1
    assert margins[0].cost_available is True
    assert margins[0].margin_value == 40
    assert margins[0].margin_pct == 40.0


def test_product_margin_without_cost_marked_unavailable():
    margins = compute_product_margins([_record("Produto B", "SKU2", 100, None)])

    assert margins[0].cost_available is False
    assert margins[0].margin_pct is None


def test_aggregate_margin_only_considers_known_cost_products():
    margins = compute_product_margins(
        [
            _record("Produto A", "SKU1", 100, 60),
            _record("Produto B", "SKU2", 100, None),
        ]
    )

    aggregate = compute_aggregate_margin(margins)

    assert aggregate.revenue_with_cost_known == 100
    assert aggregate.margin_value == 40
    assert aggregate.revenue_coverage_pct == 50.0
