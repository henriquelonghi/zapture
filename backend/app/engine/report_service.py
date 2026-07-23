"""Orquestra o motor completo: carrega dados normalizados do período, roda todas
as métricas, roda a priorização de insights, e monta o relatório final.

Esta é a única função que os dois canais de saída (relatório dinâmico e resumo
WhatsApp, nas próximas etapas) vão chamar — mesma lógica, sem duplicação.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy.orm import Session, joinedload

from app.engine.insights.rules import build_candidates, select_top_insights
from app.engine.insights.types import Insight
from app.engine.metrics.churned_customers import ChurnedCustomer, compute_churned_customers
from app.engine.metrics.margin import AggregateMargin, ProductMargin, compute_aggregate_margin, compute_product_margins
from app.engine.metrics.negative_margin import get_negative_margin_products
from app.engine.metrics.new_customers import NewCustomersResult, compute_new_vs_returning
from app.engine.metrics.ranking import RankingEntry, compute_ranking
from app.engine.metrics.revenue import RevenueResult, compute_revenue
from app.engine.metrics.ticket import TicketResult, compute_average_ticket
from app.engine.metrics.types import SalesRecord
from app.engine.metrics.units import UnitsResult, compute_units_sold
from app.engine.metrics.volume import VolumeResult, compute_order_volume
from app.models import DataSourceConnection, Order


@dataclass
class Report:
    period_start: date
    period_end: date
    revenue: RevenueResult
    ticket: TicketResult
    volume: VolumeResult
    units: UnitsResult
    new_customers: NewCustomersResult
    product_margins: list[ProductMargin]
    aggregate_margin: AggregateMargin
    negative_margin_products: list[ProductMargin]
    ranking_products: list[RankingEntry]
    ranking_categories: list[RankingEntry]
    churned_customers: list[ChurnedCustomer]
    insights: list[Insight]
    last_synced_at: object
    last_sync_label: str | None
    validation_warnings: list[str] = field(default_factory=list)


def _load_sales_records(db: Session, client_id: uuid.UUID, start: date, end: date) -> list[SalesRecord]:
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.client_id == client_id, Order.order_date >= start, Order.order_date <= end)
        .all()
    )
    records = []
    for order in orders:
        for item in order.items:
            records.append(
                SalesRecord(
                    order_id=str(order.id),
                    order_date=order.order_date,
                    product_id=str(item.product_id) if item.product_id else None,
                    product_name=item.product_name,
                    sku=item.sku,
                    category=item.category,
                    customer_id=str(order.customer_id) if order.customer_id else None,
                    quantity=float(item.quantity),
                    unit_price=float(item.unit_price),
                    total_price=float(item.total_price),
                    unit_cost=float(item.unit_cost) if item.unit_cost is not None else None,
                )
            )
    return records


def generate_report(db: Session, client_id: uuid.UUID, period_start: date, period_end: date) -> Report:
    period_length = (period_end - period_start).days + 1
    previous_end = period_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_length - 1)

    current_records = _load_sales_records(db, client_id, period_start, period_end)
    previous_records = _load_sales_records(db, client_id, previous_start, previous_end)
    full_history = _load_sales_records(db, client_id, date.min, period_end)

    revenue = compute_revenue(current_records, previous_records)
    ticket = compute_average_ticket(current_records, previous_records)
    volume = compute_order_volume(current_records, previous_records)
    units = compute_units_sold(current_records, previous_records)

    product_margins = compute_product_margins(current_records)
    aggregate_margin = compute_aggregate_margin(product_margins)
    negative_margin_products = get_negative_margin_products(product_margins)

    ranking_products = compute_ranking(current_records, previous_records, "product")
    ranking_categories = compute_ranking(current_records, previous_records, "category")

    churned_customers = compute_churned_customers(full_history, as_of=period_end)
    new_customers = compute_new_vs_returning(current_records, full_history, period_start=period_start)

    candidates = build_candidates(
        revenue=revenue,
        ticket=ticket,
        volume=volume,
        ranking=ranking_products,
        negative_margin_products=negative_margin_products,
        churned_customers=churned_customers,
    )
    insights = select_top_insights(candidates)

    data_source = (
        db.query(DataSourceConnection)
        .filter(DataSourceConnection.client_id == client_id)
        .order_by(DataSourceConnection.last_synced_at.desc().nullslast())
        .first()
    )

    return Report(
        period_start=period_start,
        period_end=period_end,
        revenue=revenue,
        ticket=ticket,
        volume=volume,
        units=units,
        new_customers=new_customers,
        product_margins=product_margins,
        aggregate_margin=aggregate_margin,
        negative_margin_products=negative_margin_products,
        ranking_products=ranking_products,
        ranking_categories=ranking_categories,
        churned_customers=churned_customers,
        insights=insights,
        last_synced_at=data_source.last_synced_at if data_source else None,
        last_sync_label=data_source.last_sync_label if data_source else None,
    )
