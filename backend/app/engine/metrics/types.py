from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class SalesRecord:
    """Um item de pedido já normalizado — a unidade de entrada de todas as métricas.

    Funções de métrica são puras (sem I/O): recebem listas de SalesRecord já
    carregadas do banco pelo report_service, o que as torna fáceis de testar
    isoladamente com fixtures.
    """

    order_id: str
    order_date: date
    product_id: str | None
    product_name: str
    sku: str | None
    category: str | None
    customer_id: str | None
    quantity: float
    unit_price: float
    total_price: float
    unit_cost: float | None
