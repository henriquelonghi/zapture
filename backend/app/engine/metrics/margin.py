from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class ProductMargin:
    product_key: str
    product_name: str
    revenue: float
    cost: float
    margin_value: float
    margin_pct: float | None
    cost_available: bool


@dataclass(frozen=True)
class AggregateMargin:
    revenue_with_cost_known: float
    cost_total: float
    margin_value: float
    margin_pct: float | None
    revenue_coverage_pct: float


def compute_product_margins(records: list[SalesRecord]) -> list[ProductMargin]:
    """Agrupa por SKU (ou product_id/nome, na ausência de SKU). Nunca assume custo
    zero: se algum item do produto não tem custo conhecido, o produto inteiro fica
    marcado como cost_available=False em vez de gerar uma margem furada."""

    grouped: dict[str, dict] = {}
    for r in records:
        key = r.sku or r.product_id or r.product_name
        bucket = grouped.setdefault(key, {"name": r.product_name, "revenue": 0.0, "cost": 0.0, "cost_available": True})
        bucket["revenue"] += r.total_price
        if r.unit_cost is None:
            bucket["cost_available"] = False
        else:
            bucket["cost"] += r.unit_cost * r.quantity

    results = []
    for key, bucket in grouped.items():
        revenue = round(bucket["revenue"], 2)
        cost_available = bucket["cost_available"]
        cost = round(bucket["cost"], 2) if cost_available else 0.0
        margin_value = round(revenue - cost, 2) if cost_available else 0.0
        margin_pct = round(margin_value / revenue * 100, 2) if cost_available and revenue else None
        results.append(
            ProductMargin(
                product_key=key,
                product_name=bucket["name"],
                revenue=revenue,
                cost=cost,
                margin_value=margin_value,
                margin_pct=margin_pct,
                cost_available=cost_available,
            )
        )
    return results


def compute_aggregate_margin(product_margins: list[ProductMargin]) -> AggregateMargin:
    known = [p for p in product_margins if p.cost_available]
    total_revenue_all = sum(p.revenue for p in product_margins)
    revenue_known = sum(p.revenue for p in known)
    cost_known = sum(p.cost for p in known)
    margin_value = round(revenue_known - cost_known, 2)
    margin_pct = round(margin_value / revenue_known * 100, 2) if revenue_known else None
    coverage_pct = round(revenue_known / total_revenue_all * 100, 2) if total_revenue_all else 0.0

    return AggregateMargin(
        revenue_with_cost_known=round(revenue_known, 2),
        cost_total=round(cost_known, 2),
        margin_value=margin_value,
        margin_pct=margin_pct,
        revenue_coverage_pct=coverage_pct,
    )
