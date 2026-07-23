from datetime import date

from app.engine.metrics.ranking import compute_ranking
from app.engine.metrics.types import SalesRecord


def _record(product_name, category, total_price):
    return SalesRecord(
        order_id="1",
        order_date=date(2026, 7, 1),
        product_id=None,
        product_name=product_name,
        sku=None,
        category=category,
        customer_id=None,
        quantity=1,
        unit_price=total_price,
        total_price=total_price,
        unit_cost=None,
    )


def test_ranking_sorted_by_variation_magnitude():
    current = [_record("A", "Cat1", 200), _record("B", "Cat1", 10)]
    previous = [_record("A", "Cat1", 100), _record("B", "Cat1", 100)]

    result = compute_ranking(current, previous, "product")

    assert result[0].name == "A"
    assert result[0].variation_abs == 100
    assert result[1].name == "B"
    assert result[1].variation_abs == -90


def test_ranking_by_category_groups_products():
    current = [_record("A", "Cat1", 100), _record("B", "Cat1", 50)]
    previous = []

    result = compute_ranking(current, previous, "category")

    assert len(result) == 1
    assert result[0].name == "Cat1"
    assert result[0].revenue_current == 150
