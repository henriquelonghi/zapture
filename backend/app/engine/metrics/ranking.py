from dataclasses import dataclass
from typing import Literal

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class RankingEntry:
    name: str
    revenue_current: float
    revenue_previous: float
    variation_pct: float | None
    variation_abs: float


def _group_revenue(records: list[SalesRecord], group_by: Literal["product", "category"]) -> dict[str, float]:
    grouped: dict[str, float] = {}
    for r in records:
        key = r.product_name if group_by == "product" else (r.category or "Sem categoria")
        grouped[key] = grouped.get(key, 0.0) + r.total_price
    return grouped


def compute_ranking(
    current: list[SalesRecord], previous: list[SalesRecord], group_by: Literal["product", "category"] = "product"
) -> list[RankingEntry]:
    """Ranking por variação (subiu/caiu), ordenado pela magnitude absoluta da mudança em R$."""

    current_grouped = _group_revenue(current, group_by)
    previous_grouped = _group_revenue(previous, group_by)

    names = set(current_grouped) | set(previous_grouped)
    entries = []
    for name in names:
        revenue_current = round(current_grouped.get(name, 0.0), 2)
        revenue_previous = round(previous_grouped.get(name, 0.0), 2)
        variation_abs = round(revenue_current - revenue_previous, 2)
        variation_pct = round(variation_abs / revenue_previous * 100, 2) if revenue_previous else None
        entries.append(
            RankingEntry(
                name=name,
                revenue_current=revenue_current,
                revenue_previous=revenue_previous,
                variation_pct=variation_pct,
                variation_abs=variation_abs,
            )
        )

    entries.sort(key=lambda e: abs(e.variation_abs), reverse=True)
    return entries
