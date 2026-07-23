import base64
import hashlib
import hmac

import app.api.routes.integrations as integrations_mod
import app.integrations.mercado_livre as ml_mod
import app.integrations.nuvemshop as ns_mod
import app.integrations.oauth_state as oauth_state_mod
import app.integrations.shopify as shopify_mod
from app.models import DataSourceConnection, DataSourceType


class _FakeSettings:
    def __init__(self):
        self.shopify_api_key = "shopify_key"
        self.shopify_api_secret = "shopify_secret"
        self.shopify_scopes = "read_orders"
        self.mercadolivre_client_id = "ml_id"
        self.mercadolivre_client_secret = "ml_secret"
        self.nuvemshop_client_id = "ns_id"
        self.nuvemshop_client_secret = "ns_secret"
        self.backend_public_url = "https://api.example.com"
        self.internal_signing_secret = "supersecret"
        self.frontend_origin = "http://localhost:5173"


def _patch_settings(monkeypatch):
    fake = _FakeSettings()
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: fake)
    monkeypatch.setattr(ml_mod, "get_settings", lambda: fake)
    monkeypatch.setattr(ns_mod, "get_settings", lambda: fake)
    monkeypatch.setattr(oauth_state_mod, "get_settings", lambda: fake)
    monkeypatch.setattr(integrations_mod, "get_settings", lambda: fake)
    return fake


def test_shopify_authorize_without_config_returns_500(api_client):
    response = api_client.get("/integrations/shopify/authorize", params={"shop": "loja.myshopify.com"})

    assert response.status_code == 500


def test_shopify_authorize_returns_url(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.get("/integrations/shopify/authorize", params={"shop": "loja.myshopify.com"})

    assert response.status_code == 200
    assert "loja.myshopify.com" in response.json()["authorize_url"]


def test_mercado_livre_authorize_returns_url(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.get("/integrations/mercado_livre/authorize")

    assert response.status_code == 200
    assert "auth.mercadolivre.com.br" in response.json()["authorize_url"]


def test_nuvemshop_authorize_returns_url(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.get("/integrations/nuvemshop/authorize")

    assert response.status_code == 200
    assert "tiendanube.com" in response.json()["authorize_url"]


def test_shopify_callback_creates_connection(api_client, monkeypatch, db_session, client_record):
    _patch_settings(monkeypatch)
    state = oauth_state_mod.create_state(client_record.id, "shopify")
    monkeypatch.setattr(shopify_mod, "exchange_code_for_token", lambda shop, code: "tok_abc")

    response = api_client.get(
        "/integrations/shopify/callback",
        params={"code": "code123", "shop": "loja.myshopify.com", "state": state},
        follow_redirects=False,
    )

    assert response.status_code in (302, 307)
    connection = (
        db_session.query(DataSourceConnection)
        .filter(
            DataSourceConnection.client_id == client_record.id,
            DataSourceConnection.source_type == DataSourceType.SHOPIFY,
        )
        .first()
    )
    assert connection is not None
    assert connection.config["access_token"] == "tok_abc"
    assert connection.config["shop_domain"] == "loja.myshopify.com"


def test_shopify_callback_with_invalid_state_returns_400(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.get(
        "/integrations/shopify/callback",
        params={"code": "code123", "shop": "loja.myshopify.com", "state": "garbage"},
    )

    assert response.status_code == 400


def test_shopify_webhook_rejects_invalid_signature(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.post(
        "/webhooks/shopify/orders",
        json={"id": 1},
        headers={"x-shopify-hmac-sha256": "invalid"},
    )

    assert response.status_code == 401


def test_shopify_webhook_ignores_unconnected_shop(api_client, monkeypatch):
    fake = _patch_settings(monkeypatch)
    body = b'{"id": 1, "line_items": []}'
    digest = hmac.new(fake.shopify_api_secret.encode(), body, hashlib.sha256).digest()
    header = base64.b64encode(digest).decode()

    response = api_client.post(
        "/webhooks/shopify/orders",
        content=body,
        headers={
            "x-shopify-hmac-sha256": header,
            "x-shopify-shop-domain": "loja.myshopify.com",
            "content-type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_shopify_webhook_ingests_order_for_connected_shop(api_client, monkeypatch, db_session, client_record):
    fake = _patch_settings(monkeypatch)
    connection = DataSourceConnection(
        client_id=client_record.id,
        source_type=DataSourceType.SHOPIFY,
        config={"access_token": "tok", "shop_domain": "loja.myshopify.com"},
    )
    db_session.add(connection)
    db_session.commit()

    body = (
        b'{"id": 555, "created_at": "2026-07-10T10:00:00-03:00", "customer": {"id": 9}, '
        b'"line_items": [{"title": "Produto A", "sku": "SKU-A", "quantity": 2, "price": "50.00"}]}'
    )
    digest = hmac.new(fake.shopify_api_secret.encode(), body, hashlib.sha256).digest()
    header = base64.b64encode(digest).decode()

    response = api_client.post(
        "/webhooks/shopify/orders",
        content=body,
        headers={
            "x-shopify-hmac-sha256": header,
            "x-shopify-shop-domain": "loja.myshopify.com",
            "content-type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_mercado_livre_webhook_ignores_unconnected_account(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.post(
        "/webhooks/mercado_livre/orders",
        json={"user_id": 123, "resource": "/orders/999", "topic": "orders_v2"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_nuvemshop_webhook_ignores_unconnected_store(api_client, monkeypatch):
    _patch_settings(monkeypatch)

    response = api_client.post(
        "/webhooks/nuvemshop/orders",
        json={"store_id": 123, "id": 999, "event": "order/created"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
