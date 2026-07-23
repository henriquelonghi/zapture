from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class UnitsResult:
    units_current: float
    units_previous: float
    variation_pct: float | None


def compute_units_sold(current: list[SalesRecord], previous: list[SalesRecord]) -> UnitsResult:
    units_current = round(sum(r.quantity for r in current), 2)
    units_previous = round(sum(r.quantity for r in previous), 2)

    variation_pct = None
    if units_previous:
        variation_pct = round((units_current - units_previous) / units_previous * 100, 2)

    return UnitsResult(units_current=units_current, units_previous=units_previous, variation_pct=variation_pct)
