import uuid

import app.integrations.oauth_state as oauth_state


class _FakeSettings:
    def __init__(self, secret=None):
        self.internal_signing_secret = secret


def test_create_and_decode_state_roundtrip(monkeypatch):
    monkeypatch.setattr(oauth_state, "get_settings", lambda: _FakeSettings(secret="topsecret"))
    client_id = uuid.uuid4()

    state = oauth_state.create_state(client_id, "shopify")
    assert state is not None

    decoded = oauth_state.decode_state(state, "shopify")
    assert decoded == client_id


def test_decode_state_rejects_wrong_platform(monkeypatch):
    monkeypatch.setattr(oauth_state, "get_settings", lambda: _FakeSettings(secret="topsecret"))
    state = oauth_state.create_state(uuid.uuid4(), "shopify")

    assert oauth_state.decode_state(state, "mercado_livre") is None


def test_create_state_returns_none_without_secret(monkeypatch):
    monkeypatch.setattr(oauth_state, "get_settings", lambda: _FakeSettings(secret=None))

    assert oauth_state.create_state(uuid.uuid4(), "shopify") is None


def test_decode_state_returns_none_for_garbage(monkeypatch):
    monkeypatch.setattr(oauth_state, "get_settings", lambda: _FakeSettings(secret="topsecret"))

    assert oauth_state.decode_state("not-a-real-token", "shopify") is None
