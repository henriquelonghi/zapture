"""Integração com Stripe: sessão de checkout do plano único + verificação do
webhook que confirma pagamento. Sem STRIPE_SECRET_KEY configurado, degrada
graciosamente (mesmo padrão de whatsapp_client.py e das integrações de
plataforma) — checkout retorna None em vez de quebrar."""

import stripe

from app.core.config import get_settings


def create_checkout_session(
    client_id: str,
    existing_stripe_customer_id: str | None,
    success_url: str,
    cancel_url: str,
) -> dict | None:
    """Retorna {"checkout_url": ..., "customer_id": ...} ou None se o Stripe
    não estiver configurado ou a chamada falhar."""
    settings = get_settings()
    if not settings.stripe_secret_key or not settings.stripe_price_id:
        return None

    stripe.api_key = settings.stripe_secret_key
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
            client_reference_id=client_id,
            customer=existing_stripe_customer_id,
        )
    except stripe.StripeError:
        return None

    return {"checkout_url": session.url, "customer_id": session.customer}


def verify_webhook_event(payload: bytes, signature: str | None) -> stripe.Event | None:
    settings = get_settings()
    if not settings.stripe_webhook_secret or not signature:
        return None
    try:
        return stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except (stripe.SignatureVerificationError, ValueError):
        return None
