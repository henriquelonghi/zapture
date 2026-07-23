from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class VolumeResult:
    orders_current: int
    orders_previous: int
    variation_pct: float | None


def compute_order_volume(current: list[SalesRecord], previous: list[SalesRecord]) -> VolumeResult:
    orders_current = len({r.order_id for r in current})
    orders_previous = len({r.order_id for r in previous})

    variation_pct = None
    if orders_previous:
        variation_pct = round((orders_current - orders_previous) / orders_previous * 100, 2)

    return VolumeResult(orders_current=orders_current, orders_previous=orders_previous, variation_pct=variation_pct)
