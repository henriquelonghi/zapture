"""Priorização de insights — o ponto do motor com mais ambiguidade no documento
(ele define que os 2-3 mais relevantes devem ser escolhidos, mas não como).

Primeira versão explícita, pensada para ser recalibrada com dados reais:
- cada métrica gera candidatos com um score de relevância (magnitude % de
  variação, ou um score-base fixo para alertas categóricos como margem
  negativa e clientes sumidos);
- margem negativa tem prioridade alta fixa — é o gancho de venda citado no
  documento;
- a seleção final evita repetir a mesma categoria de insight quando existe
  alternativa diversa, mas nunca entrega menos que `min_n` insights se
  houver candidatos suficientes.
"""

from app.engine.insights.types import Insight
from app.engine.metrics.churned_customers import ChurnedCustomer
from app.engine.metrics.margin import ProductMargin
from app.engine.metrics.ranking import RankingEntry
from app.engine.metrics.revenue import RevenueResult
from app.engine.metrics.ticket import TicketResult
from app.engine.metrics.volume import VolumeResult

NEGATIVE_MARGIN_BASE_SCORE = 90.0
CHURNED_CUSTOMERS_BASE_SCORE = 70.0


def _direction_word(variation_pct: float) -> str:
    return "subiu" if variation_pct >= 0 else "caiu"


def build_candidates(
    revenue: RevenueResult,
    ticket: TicketResult,
    volume: VolumeResult,
    ranking: list[RankingEntry],
    negative_margin_products: list[ProductMargin],
    churned_customers: list[ChurnedCustomer],
) -> list[Insight]:
    candidates: list[Insight] = []

    if revenue.variation_pct is not None:
        candidates.append(
            Insight(
                key="revenue_variation",
                category="faturamento",
                title=f"Faturamento {_direction_word(revenue.variation_pct)} {abs(revenue.variation_pct):.1f}%",
                description=(
                    f"Faturamento do período: R$ {revenue.total_current:,.2f} "
                    f"({revenue.variation_pct:+.1f}% vs. período anterior)."
                ),
                score=abs(revenue.variation_pct),
            )
        )

    if ticket.variation_pct is not None:
        candidates.append(
            Insight(
                key="ticket_variation",
                category="ticket_medio",
                title=f"Ticket médio {_direction_word(ticket.variation_pct)} {abs(ticket.variation_pct):.1f}%",
                description=f"Ticket médio atual: R$ {ticket.average_current:,.2f}.",
                score=abs(ticket.variation_pct) * 0.8,
            )
        )

    if volume.variation_pct is not None:
        candidates.append(
            Insight(
                key="volume_variation",
                category="pedidos",
                title=f"Número de pedidos {_direction_word(volume.variation_pct)} {abs(volume.variation_pct):.1f}%",
                description=f"{volume.orders_current} pedidos no período.",
                score=abs(volume.variation_pct) * 0.7,
            )
        )

    for entry in ranking[:3]:
        if entry.variation_pct is None:
            continue
        candidates.append(
            Insight(
                key=f"ranking_{entry.name}",
                category="ranking",
                title=f"{entry.name} {_direction_word(entry.variation_pct)} {abs(entry.variation_pct):.1f}%",
                description=(
                    f"R$ {entry.revenue_current:,.2f} no período "
                    f"({entry.variation_pct:+.1f}% vs. anterior)."
                ),
                score=min(abs(entry.variation_pct) * 0.6, 85.0),
            )
        )

    for product in negative_margin_products[:3]:
        candidates.append(
            Insight(
                key=f"negative_margin_{product.product_key}",
                category="margem_negativa",
                title=f"{product.product_name} está com margem negativa",
                description=f"Margem de R$ {product.margin_value:,.2f} ({product.margin_pct:.1f}%) no período.",
                score=NEGATIVE_MARGIN_BASE_SCORE + min(abs(product.margin_value), 10),
            )
        )

    if churned_customers:
        candidates.append(
            Insight(
                key="churned_customers",
                category="clientes_sumidos",
                title=f"{len(churned_customers)} cliente(s) sumiram",
                description="Clientes que não compram há mais tempo que o padrão histórico deles.",
                score=CHURNED_CUSTOMERS_BASE_SCORE + min(len(churned_customers), 10),
            )
        )

    return candidates


def select_top_insights(candidates: list[Insight], min_n: int = 2, max_n: int = 3) -> list[Insight]:
    ordered = sorted(candidates, key=lambda i: i.score, reverse=True)

    selected: list[Insight] = []
    used_categories: set[str] = set()

    for insight in ordered:
        if len(selected) >= max_n:
            break
        if insight.category in used_categories:
            continue
        selected.append(insight)
        used_categories.add(insight.category)

    if len(selected) < min_n:
        for insight in ordered:
            if len(selected) >= min_n:
                break
            if insight not in selected:
                selected.append(insight)

    return selected[:max_n]
