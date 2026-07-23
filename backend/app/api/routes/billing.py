"""Plano único (R$ 47/mês, mesmo valor da landing page) + checkout via
Stripe. Enquanto STRIPE_SECRET_KEY/STRIPE_PRICE_ID não estiverem
configurados, /billing/checkout responde 500 — mesmo padrão de degradação
graciosa das outras integrações (WhatsApp, Shopify, etc)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.billing.stripe_client import create_checkout_session, verify_webhook_event
from app.core.config import get_settings
from app.models import Client
from app.schemas.billing import CheckoutSessionOut, PlanOut

router = APIRouter(tags=["billing"])

_SINGLE_PLAN = PlanOut(id="mensal", name="Plano mensal", price_cents=4700, currency="BRL", interval="month")


def _parse_uuid(value: str | None) -> uuid.UUID | None:
    if not value:
        return None
    try:
        return uuid.UUID(value)
    except ValueError:
        return None


@router.get("/billing/plans", response_model=list[PlanOut])
def list_plans() -> list[PlanOut]:
    return [_SINGLE_PLAN]


@router.post("/billing/checkout", response_model=CheckoutSessionOut)
def create_checkout(
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> CheckoutSessionOut:
    settings = get_settings()
    result = create_checkout_session(
        client_id=str(client.id),
        existing_stripe_customer_id=client.stripe_customer_id,
        success_url=f"{settings.frontend_origin}/plano?checkout=sucesso",
        cancel_url=f"{settings.frontend_origin}/plano?checkout=cancelado",
    )
    if result is None:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Pagamento não configurado no servidor.")

    if result.get("customer_id") and not client.stripe_customer_id:
        client.stripe_customer_id = result["customer_id"]
        db.commit()

    return CheckoutSessionOut(checkout_url=result["checkout_url"])


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    raw_body = await request.body()
    signature = request.headers.get("stripe-signature")
    event = verify_webhook_event(raw_body, signature)
    if event is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Assinatura inválida.")

    data = event["data"]["object"]

    if event["type"] == "checkout.session.completed":
        client_id = _parse_uuid(data.get("client_reference_id"))
        target = db.query(Client).filter(Client.id == client_id).first() if client_id else None
        if target is not None:
            target.stripe_customer_id = data.get("customer") or target.stripe_customer_id
            target.stripe_subscription_id = data.get("subscription")
            target.plan_status = "active"
            db.commit()

    elif event["type"] in ("customer.subscription.updated", "customer.subscription.deleted"):
        subscription_id = data.get("id")
        target = db.query(Client).filter(Client.stripe_subscription_id == subscription_id).first()
        if target is not None:
            target.plan_status = data.get("status", "canceled")
            db.commit()

    return {"status": "ok"}
