from datetime import date, datetime

from pydantic import BaseModel


class RevenueOut(BaseModel):
    total_current: float
    total_previous: float
    variation_pct: float | None


class TicketOut(BaseModel):
    average_current: float | None
    average_previous: float | None
    variation_pct: float | None


class VolumeOut(BaseModel):
    orders_current: int
    orders_previous: int
    variation_pct: float | None


class UnitsOut(BaseModel):
    units_current: float
    units_previous: float
    variation_pct: float | None


class NewCustomersOut(BaseModel):
    new_customers_count: int
    returning_customers_count: int
    new_customers_revenue: float
    returning_customers_revenue: float


class ProductMarginOut(BaseModel):
    product_key: str
    product_name: str
    revenue: float
    cost: float
    margin_value: float
    margin_pct: float | None
    cost_available: bool


class AggregateMarginOut(BaseModel):
    revenue_with_cost_known: float
    cost_total: float
    margin_value: float
    margin_pct: float | None
    revenue_coverage_pct: float


class RankingEntryOut(BaseModel):
    name: str
    revenue_current: float
    revenue_previous: float
    variation_pct: float | None
    variation_abs: float


class ChurnedCustomerOut(BaseModel):
    customer_id: str
    last_purchase_at: date
    days_since_last_purchase: int
    avg_interval_days: float


class InsightOut(BaseModel):
    key: str
    category: str
    title: str
    description: str
    score: float


class ReportOut(BaseModel):
    period_start: date
    period_end: date
    revenue: RevenueOut
    ticket: TicketOut
    volume: VolumeOut
    units: UnitsOut
    new_customers: NewCustomersOut
    product_margins: list[ProductMarginOut]
    aggregate_margin: AggregateMarginOut
    negative_margin_products: list[ProductMarginOut]
    ranking_products: list[RankingEntryOut]
    ranking_categories: list[RankingEntryOut]
    churned_customers: list[ChurnedCustomerOut]
    insights: list[InsightOut]
    last_synced_at: datetime | None
    last_sync_label: str | None
    validation_warnings: list[str]
