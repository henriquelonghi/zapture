import httpx

import app.notifications.whatsapp_client as wc


class _FakeSettings:
    def __init__(self, token=None, phone_number_id=None):
        self.whatsapp_api_token = token
        self.whatsapp_phone_number_id = phone_number_id
        self.whatsapp_api_base_url = "https://example.com"


def test_send_whatsapp_message_returns_false_without_credentials(monkeypatch):
    monkeypatch.setattr(wc, "get_settings", lambda: _FakeSettings())

    assert wc.send_whatsapp_message("5511999998888", "oi") is False


def test_send_whatsapp_message_success(monkeypatch):
    monkeypatch.setattr(wc, "get_settings", lambda: _FakeSettings(token="token123", phone_number_id="123456"))

    class FakeResponse:
        def raise_for_status(self):
            pass

    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["headers"] = headers
        return FakeResponse()

    monkeypatch.setattr(wc.httpx, "post", fake_post)

    assert wc.send_whatsapp_message("5511999998888", "oi") is True
    assert captured["url"] == "https://example.com/123456/messages"
    assert captured["headers"]["Authorization"] == "Bearer token123"


def test_send_whatsapp_message_handles_http_error(monkeypatch):
    monkeypatch.setattr(wc, "get_settings", lambda: _FakeSettings(token="token123", phone_number_id="123456"))

    def fake_post(url, json, headers, timeout):
        raise httpx.HTTPError("boom")

    monkeypatch.setattr(wc.httpx, "post", fake_post)

    assert wc.send_whatsapp_message("5511999998888", "oi") is False
