from dataclasses import dataclass
from datetime import date

from app.engine.metrics.types import SalesRecord


@dataclass(frozen=True)
class NewCustomersResult:
    new_customers_count: int
    returning_customers_count: int
    new_customers_revenue: float
    returning_customers_revenue: float


def compute_new_vs_returning(
    current: list[SalesRecord], full_history: list[SalesRecord], period_start: date
) -> NewCustomersResult:
    """Um cliente é 'novo' se a primeira compra dele em toda a história (não só
    no período atual) caiu dentro do período. `full_history` precisa cobrir tudo
    até o fim do período pra essa comparação fazer sentido."""

    first_purchase: dict[str, date] = {}
    for r in full_history:
        if not r.customer_id:
            continue
        current_first = first_purchase.get(r.customer_id)
        if current_first is None or r.order_date < current_first:
            first_purchase[r.customer_id] = r.order_date

    new_customers: set[str] = set()
    returning_customers: set[str] = set()
    new_revenue = 0.0
    returning_revenue = 0.0

    for r in current:
        if not r.customer_id:
            continue
        is_new = first_purchase.get(r.customer_id, r.order_date) >= period_start
        if is_new:
            new_customers.add(r.customer_id)
            new_revenue += r.total_price
        else:
            returning_customers.add(r.customer_id)
            returning_revenue += r.total_price

    return NewCustomersResult(
        new_customers_count=len(new_customers),
        returning_customers_count=len(returning_customers),
        new_customers_revenue=round(new_revenue, 2),
        returning_customers_revenue=round(returning_revenue, 2),
    )
