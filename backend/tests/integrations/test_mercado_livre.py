import app.integrations.mercado_livre as ml_mod


class _FakeSettings:
    def __init__(self, client_id=None, client_secret=None, backend_public_url=None):
        self.mercadolivre_client_id = client_id
        self.mercadolivre_client_secret = client_secret
        self.backend_public_url = backend_public_url


def test_build_authorize_url_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(ml_mod, "get_settings", lambda: _FakeSettings())

    assert ml_mod.build_authorize_url("state123") is None


def test_build_authorize_url_includes_expected_params(monkeypatch):
    monkeypatch.setattr(
        ml_mod,
        "get_settings",
        lambda: _FakeSettings(client_id="id123", backend_public_url="https://api.example.com"),
    )

    url = ml_mod.build_authorize_url("state123")

    assert url is not None
    assert "client_id=id123" in url
    assert "state=state123" in url


def test_exchange_code_for_token_success(monkeypatch):
    monkeypatch.setattr(
        ml_mod,
        "get_settings",
        lambda: _FakeSettings(client_id="id123", client_secret="secret123", backend_public_url="https://api.example.com"),
    )

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"access_token": "tok_abc", "user_id": 555}

    monkeypatch.setattr(ml_mod.httpx, "post", lambda url, data, timeout: FakeResponse())

    assert ml_mod.exchange_code_for_token("code123") == {"access_token": "tok_abc", "user_id": "555"}


def test_exchange_code_for_token_returns_none_without_config(monkeypatch):
    monkeypatch.setattr(ml_mod, "get_settings", lambda: _FakeSettings())

    assert ml_mod.exchange_code_for_token("code123") is None


def test_fetch_order_success(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"id": 1, "order_items": []}

    monkeypatch.setattr(ml_mod.httpx, "get", lambda url, headers, timeout: FakeResponse())

    assert ml_mod.fetch_order("tok_abc", "1") == {"id": 1, "order_items": []}


def test_map_order_payload_extracts_items():
    order = {
        "id": 2001,
        "date_created": "2026-07-10T10:00:00.000-04:00",
        "buyer": {"id": 42},
        "order_items": [
            {"item": {"title": "Produto ML", "seller_sku": "SKU-ML"}, "quantity": 3, "unit_price": 25.5},
        ],
    }

    rows = ml_mod.map_order_payload(order)

    assert len(rows) == 1
    row = rows[0]
    assert row["pedido_id"] == "2001"
    assert row["data_pedido"] == "2026-07-10"
    assert row["produto"] == "Produto ML"
    assert row["sku"] == "SKU-ML"
    assert row["quantidade"] == 3
    assert row["valor_unitario"] == 25.5
    assert row["cliente_id"] == "42"
