from dataclasses import dataclass

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class TicketResult:
    average_current: float | None
    average_previous: float | None
    variation_pct: float | None


def _average_ticket(records: list[SalesRecord]) -> float | None:
    orders: dict[str, float] = {}
    for r in records:
        orders[r.order_id] = orders.get(r.order_id, 0.0) + r.total_price
    if not orders:
        return None
    return round(sum(orders.values()) / len(orders), 2)


def compute_average_ticket(current: list[SalesRecord], previous: list[SalesRecord]) -> TicketResult:
    average_current = _average_ticket(current)
    average_previous = _average_ticket(previous)

    variation_pct = None
    if average_previous:
        variation_pct = round(((average_current or 0) - average_previous) / average_previous * 100, 2)

    return TicketResult(average_current=average_current, average_previous=average_previous, variation_pct=variation_pct)
