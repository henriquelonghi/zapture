from app.engine.metrics.margin import ProductMargin


def get_negative_margin_products(product_margins: list[ProductMargin]) -> list[ProductMargin]:
    """Alerta prioritário do documento: produtos vendendo no prejuízo. Só considera
    produtos com custo conhecido (nunca infere prejuízo de um custo ausente)."""

    return sorted(
        (p for p in product_margins if p.cost_available and p.margin_value < 0),
        key=lambda p: p.margin_value,
    )
