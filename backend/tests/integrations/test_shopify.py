import base64
import hashlib
import hmac

import app.integrations.shopify as shopify_mod


class _FakeSettings:
    def __init__(self, api_key=None, api_secret=None, backend_public_url=None, scopes="read_orders"):
        self.shopify_api_key = api_key
        self.shopify_api_secret = api_secret
        self.backend_public_url = backend_public_url
        self.shopify_scopes = scopes


def test_build_authorize_url_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: _FakeSettings())

    assert shopify_mod.build_authorize_url("loja.myshopify.com", "state123") is None


def test_build_authorize_url_includes_expected_params(monkeypatch):
    monkeypatch.setattr(
        shopify_mod,
        "get_settings",
        lambda: _FakeSettings(api_key="key123", backend_public_url="https://api.example.com"),
    )

    url = shopify_mod.build_authorize_url("loja.myshopify.com", "state123")

    assert url is not None
    assert url.startswith("https://loja.myshopify.com/admin/oauth/authorize?")
    assert "client_id=key123" in url
    assert "state=state123" in url


def test_exchange_code_for_token_success(monkeypatch):
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: _FakeSettings(api_key="key123", api_secret="secret123"))

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"access_token": "tok_abc"}

    monkeypatch.setattr(shopify_mod.httpx, "post", lambda url, json, timeout: FakeResponse())

    assert shopify_mod.exchange_code_for_token("loja.myshopify.com", "code123") == "tok_abc"


def test_exchange_code_for_token_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: _FakeSettings())

    assert shopify_mod.exchange_code_for_token("loja.myshopify.com", "code123") is None


def test_verify_webhook_hmac_accepts_valid_signature(monkeypatch):
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: _FakeSettings(api_secret="secret123"))
    body = b'{"id": 1}'
    digest = hmac.new(b"secret123", body, hashlib.sha256).digest()
    header = base64.b64encode(digest).decode()

    assert shopify_mod.verify_webhook_hmac(body, header) is True


def test_verify_webhook_hmac_rejects_invalid_signature(monkeypatch):
    monkeypatch.setattr(shopify_mod, "get_settings", lambda: _FakeSettings(api_secret="secret123"))

    assert shopify_mod.verify_webhook_hmac(b'{"id": 1}', "garbage") is False


def test_map_order_payload_extracts_line_items():
    payload = {
        "id": 12345,
        "created_at": "2026-07-10T10:00:00-03:00",
        "customer": {"id": 999},
        "line_items": [
            {"title": "Produto A", "sku": "SKU-A", "quantity": 2, "price": "50.00"},
        ],
    }

    rows = shopify_mod.map_order_payload(payload)

    assert len(rows) == 1
    row = rows[0]
    assert row["pedido_id"] == "12345"
    assert row["data_pedido"] == "2026-07-10"
    assert row["produto"] == "Produto A"
    assert row["sku"] == "SKU-A"
    assert row["quantidade"] == 2
    assert row["valor_unitario"] == "50.00"
    assert row["cliente_id"] == "999"


def test_map_order_payload_skips_items_without_quantity_or_price():
    payload = {"id": 1, "created_at": "2026-07-10T10:00:00Z", "line_items": [{"title": "Sem preço"}]}

    assert shopify_mod.map_order_payload(payload) == []
