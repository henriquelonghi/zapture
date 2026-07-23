export interface PlanOut {
  id: string
  name: string
  price_cents: number
  currency: string
  interval: string
}

export interface CheckoutSessionOut {
  checkout_url: string
}
