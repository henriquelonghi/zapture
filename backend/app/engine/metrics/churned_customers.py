from dataclasses import dataclass
from datetime import date

from app.engine.metrics.types import SalesRecord

DEFAULT_MULTIPLIER = 1.5
DEFAULT_MIN_DAYS_FLOOR = 14
DEFAULT_MIN_ORDERS = 2


@dataclass(frozen=True)
class ChurnedCustomer:
    customer_id: str
    last_purchase_at: date
    days_since_last_purchase: int
    avg_interval_days: float


def compute_churned_customers(
    full_history: list[SalesRecord],
    as_of: date,
    multiplier: float = DEFAULT_MULTIPLIER,
    min_days_floor: int = DEFAULT_MIN_DAYS_FLOOR,
    min_orders: int = DEFAULT_MIN_ORDERS,
) -> list[ChurnedCustomer]:
    """Compara o intervalo desde a última compra com o padrão histórico do próprio
    cliente (não um limite fixo pra todos). Clientes com menos de `min_orders`
    pedidos não têm histórico suficiente pra estimar um padrão e são ignorados."""

    purchases_by_customer: dict[str, list[date]] = {}
    for r in full_history:
        if not r.customer_id:
            continue
        purchases_by_customer.setdefault(r.customer_id, []).append(r.order_date)

    results = []
    for customer_id, dates in purchases_by_customer.items():
        unique_dates = sorted(set(dates))
        if len(unique_dates) < min_orders:
            continue

        intervals = [(unique_dates[i] - unique_dates[i - 1]).days for i in range(1, len(unique_dates))]
        avg_interval = sum(intervals) / len(intervals)
        last_purchase = unique_dates[-1]
        days_since = (as_of - last_purchase).days

        threshold = max(avg_interval * multiplier, min_days_floor)
        if days_since > threshold:
            results.append(
                ChurnedCustomer(
                    customer_id=customer_id,
                    last_purchase_at=last_purchase,
                    days_since_last_purchase=days_since,
                    avg_interval_days=round(avg_interval, 1),
                )
            )

    results.sort(key=lambda c: c.days_since_last_purchase, reverse=True)
    return results
