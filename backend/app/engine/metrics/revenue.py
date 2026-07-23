from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class RevenueResult:
    total_current: float
    total_previous: float
    variation_pct: float | None


def compute_revenue(current: list[SalesRecord], previous: list[SalesRecord]) -> RevenueResult:
    total_current = round(sum(r.total_price for r in current), 2)
    total_previous = round(sum(r.total_price for r in previous), 2)

    variation_pct = None
    if total_previous:
        variation_pct = round((total_current - total_previous) / total_previous * 100, 2)

    return RevenueResult(total_current=total_current, total_previous=total_previous, variation_pct=variation_pct)
