export interface RevenueOut {
  total_current: number
  total_previous: number
  variation_pct: number | null
}

export interface TicketOut {
  average_current: number | null
  average_previous: number | null
  variation_pct: number | null
}

export interface VolumeOut {
  orders_current: number
  orders_previous: number
  variation_pct: number | null
}

export interface UnitsOut {
  units_current: number
  units_previous: number
  variation_pct: number | null
}

export interface NewCustomersOut {
  new_customers_count: number
  returning_customers_count: number
  new_customers_revenue: number
  returning_customers_revenue: number
}

export interface ProductMarginOut {
  product_key: string
  product_name: string
  revenue: number
  cost: number
  margin_value: number
  margin_pct: number | null
  cost_available: boolean
}

export interface AggregateMarginOut {
  revenue_with_cost_known: number
  cost_total: number
  margin_value: number
  margin_pct: number | null
  revenue_coverage_pct: number
}

export interface RankingEntryOut {
  name: string
  revenue_current: number
  revenue_previous: number
  variation_pct: number | null
  variation_abs: number
}

export interface BestsellerOut {
  product_key: string
  product_name: string
  units_sold: number
  revenue: number
}

export interface HighestPricedSaleOut {
  product_key: string
  product_name: string
  unit_price: number
  order_id: string
}

export interface ChurnedCustomerOut {
  customer_id: string
  last_purchase_at: string
  days_since_last_purchase: number
  avg_interval_days: number
}

export interface InsightOut {
  key: string
  category: string
  title: string
  description: string
  score: number
}

export interface ReportOut {
  period_start: string
  period_end: string
  revenue: RevenueOut
  ticket: TicketOut
  volume: VolumeOut
  units: UnitsOut
  new_customers: NewCustomersOut
  product_margins: ProductMarginOut[]
  aggregate_margin: AggregateMarginOut
  negative_margin_products: ProductMarginOut[]
  ranking_products: RankingEntryOut[]
  ranking_categories: RankingEntryOut[]
  churned_customers: ChurnedCustomerOut[]
  bestseller: BestsellerOut | null
  highest_priced_sale: HighestPricedSaleOut | null
  insights: InsightOut[]
  last_synced_at: string | null
  last_sync_label: string | null
  validation_warnings: string[]
}

export interface DataSourceOut {
  source_type: string
  last_synced_at: string | null
  last_sync_label: string | null
  last_validation_warnings: string[]
}

export interface IngestionResultOut {
  orders_created: number
  orders_updated: number
  items_created: number
  warnings: string[]
  row_errors: string[]
}
