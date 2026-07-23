from pydantic import BaseModel


class PlanOut(BaseModel):
    id: str
    name: str
    price_cents: int
    currency: str
    interval: str


class CheckoutSessionOut(BaseModel):
    checkout_url: str
