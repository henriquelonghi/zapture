import app.integrations.nuvemshop as ns_mod


class _FakeSettings:
    def __init__(self, client_id=None, client_secret=None):
        self.nuvemshop_client_id = client_id
        self.nuvemshop_client_secret = client_secret


def test_build_authorize_url_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(ns_mod, "get_settings", lambda: _FakeSettings())

    assert ns_mod.build_authorize_url("state123") is None


def test_build_authorize_url_includes_client_id_and_state(monkeypatch):
    monkeypatch.setattr(ns_mod, "get_settings", lambda: _FakeSettings(client_id="id123"))

    url = ns_mod.build_authorize_url("state123")

    assert url == "https://www.tiendanube.com/apps/id123/authorize?state=state123"


def test_exchange_code_for_token_success(monkeypatch):
    monkeypatch.setattr(ns_mod, "get_settings", lambda: _FakeSettings(client_id="id123", client_secret="secret123"))

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"access_token": "tok_abc", "user_id": 777}

    monkeypatch.setattr(ns_mod.httpx, "post", lambda url, json, timeout: FakeResponse())

    assert ns_mod.exchange_code_for_token("code123") == {"access_token": "tok_abc", "store_id": "777"}


def test_exchange_code_for_token_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(ns_mod, "get_settings", lambda: _FakeSettings())

    assert ns_mod.exchange_code_for_token("code123") is None


def test_fetch_order_success(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"id": 1, "products": []}

    monkeypatch.setattr(ns_mod.httpx, "get", lambda url, headers, timeout: FakeResponse())

    assert ns_mod.fetch_order("tok_abc", "store1", "1") == {"id": 1, "products": []}


def test_map_order_payload_extracts_products():
    order = {
        "id": 3001,
        "created_at": "2026-07-10T10:00:00+0000",
        "customer": {"id": 88},
        "products": [
            {"name": "Produto NS", "sku": "SKU-NS", "quantity": 1, "price": "99.90"},
        ],
    }

    rows = ns_mod.map_order_payload(order)

    assert len(rows) == 1
    row = rows[0]
    assert row["pedido_id"] == "3001"
    assert row["data_pedido"] == "2026-07-10"
    assert row["produto"] == "Produto NS"
    assert row["sku"] == "SKU-NS"
    assert row["quantidade"] == 1
    assert row["valor_unitario"] == "99.90"
    assert row["cliente_id"] == "88"
