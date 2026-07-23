"""Dois recortes simples de destaque do período, complementares ao ranking por
variação em ranking.py: o produto mais vendido em unidades, e o item vendido
pelo maior preço unitário. Nenhum dos dois compara com o período anterior —
são leituras do período atual, não de variação."""

from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class BestsellerResult:
    product_key: str
    product_name: str
    units_sold: float
    revenue: float


@dataclass(frozen=True)
class HighestPricedSaleResult:
    product_key: str
    product_name: str
    unit_price: float
    order_id: str


def compute_bestseller(current: list[SalesRecord]) -> BestsellerResult | None:
    """Agrupa por SKU (ou product_id/nome, na ausência de SKU) e pega quem vendeu
    mais unidades no período — mesma chave de agrupamento de margin.py."""

    if not current:
        return None

    grouped: dict[str, dict] = {}
    for r in current:
        key = r.sku or r.product_id or r.product_name
        bucket = grouped.setdefault(key, {"name": r.product_name, "units": 0.0, "revenue": 0.0})
        bucket["units"] += r.quantity
        bucket["revenue"] += r.total_price

    best_key = max(grouped, key=lambda k: grouped[k]["units"])
    best = grouped[best_key]
    return BestsellerResult(
        product_key=best_key,
        product_name=best["name"],
        units_sold=round(best["units"], 2),
        revenue=round(best["revenue"], 2),
    )


def compute_highest_priced_sale(current: list[SalesRecord]) -> HighestPricedSaleResult | None:
    """Item individual vendido pelo maior preço unitário no período (não agrupado
    por produto) — responde "qual foi a venda mais cara" em vez de "qual produto
    é o mais caro do catálogo", já que só enxergamos o que foi vendido."""

    if not current:
        return None

    top = max(current, key=lambda r: r.unit_price)
    return HighestPricedSaleResult(
        product_key=top.sku or top.product_id or top.product_name,
        product_name=top.product_name,
        unit_price=top.unit_price,
        order_id=top.order_id,
    )
