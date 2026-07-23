import app.api.routes.billing as billing_mod
from app.models import Client


def test_list_plans_returns_single_plan(api_client):
    response = api_client.get("/billing/plans")

    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 1
    assert plans[0]["price_cents"] == 4700
    assert plans[0]["currency"] == "BRL"


def test_checkout_without_stripe_configured_returns_500(api_client, monkeypatch):
    monkeypatch.setattr(billing_mod, "create_checkout_session", lambda **kwargs: None)

    response = api_client.post("/billing/checkout")

    assert response.status_code == 500


def test_checkout_returns_url_and_stores_customer_id(api_client, monkeypatch, db_session, client_record):
    monkeypatch.setattr(
        billing_mod,
        "create_checkout_session",
        lambda **kwargs: {"checkout_url": "https://checkout.stripe.com/session/abc", "customer_id": "cus_123"},
    )

    response = api_client.post("/billing/checkout")

    assert response.status_code == 200
    assert response.json()["checkout_url"] == "https://checkout.stripe.com/session/abc"
    db_session.refresh(client_record)
    assert client_record.stripe_customer_id == "cus_123"


def test_stripe_webhook_rejects_invalid_signature(api_client, monkeypatch):
    monkeypatch.setattr(billing_mod, "verify_webhook_event", lambda payload, sig: None)

    response = api_client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "bad"})

    assert response.status_code == 401


def test_stripe_webhook_activates_plan_on_checkout_completed(api_client, monkeypatch, db_session, client_record):
    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": str(client_record.id),
                "customer": "cus_456",
                "subscription": "sub_789",
            }
        },
    }
    monkeypatch.setattr(billing_mod, "verify_webhook_event", lambda payload, sig: event)

    response = api_client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "valid"})

    assert response.status_code == 200
    db_session.refresh(client_record)
    assert client_record.plan_status == "active"
    assert client_record.stripe_subscription_id == "sub_789"
    assert client_record.stripe_customer_id == "cus_456"


def test_stripe_webhook_deactivates_plan_on_subscription_deleted(api_client, monkeypatch, db_session, client_record):
    client_record.plan_status = "active"
    client_record.stripe_subscription_id = "sub_789"
    db_session.commit()

    event = {
        "type": "customer.subscription.deleted",
        "data": {"object": {"id": "sub_789", "status": "canceled"}},
    }
    monkeypatch.setattr(billing_mod, "verify_webhook_event", lambda payload, sig: event)

    response = api_client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "valid"})

    assert response.status_code == 200
    db_session.refresh(client_record)
    assert client_record.plan_status == "canceled"


def test_stripe_webhook_ignores_unknown_client_reference(api_client, monkeypatch):
    event = {
        "type": "checkout.session.completed",
        "data": {"object": {"client_reference_id": "00000000-0000-0000-0000-000000000000"}},
    }
    monkeypatch.setattr(billing_mod, "verify_webhook_event", lambda payload, sig: event)

    response = api_client.post("/webhooks/stripe", content=b"{}", headers={"stripe-signature": "valid"})

    assert response.status_code == 200
