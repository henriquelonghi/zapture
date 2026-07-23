from app.engine.metrics.margin import ProductMargin
from app.engine.metrics.negative_margin import get_negative_margin_products


def test_filters_and_sorts_negative_margin_products():
    margins = [
        ProductMargin("A", "Produto A", revenue=100, cost=60, margin_value=40, margin_pct=40.0, cost_available=True),
        ProductMargin("B", "Produto B", revenue=100, cost=120, margin_value=-20, margin_pct=-20.0, cost_available=True),
        ProductMargin("C", "Produto C", revenue=100, cost=150, margin_value=-50, margin_pct=-50.0, cost_available=True),
        ProductMargin("D", "Produto D", revenue=100, cost=0, margin_value=0, margin_pct=None, cost_available=False),
    ]

    result = get_negative_margin_products(margins)

    assert [p.product_key for p in result] == ["C", "B"]
