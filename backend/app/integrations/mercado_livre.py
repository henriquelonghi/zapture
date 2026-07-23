"""Integração com a API do Mercado Livre: OAuth + notificação de webhook
(tópico orders_v2). Diferente da Shopify, a notificação só avisa que um
recurso mudou (não manda o pedido inteiro) — é preciso buscar o pedido via
API usando o access_token guardado. A API do ML não tem campo de custo em
lugar nenhum (ver descricao.md §3): margem sempre depende de cadastro manual,
pivot pra API ou não."""

from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

_AUTHORIZE_URL = "https://auth.mercadolivre.com.br/authorization"
_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"


def build_authorize_url(state: str) -> str | None:
    settings = get_settings()
    if not settings.mercadolivre_client_id or not settings.backend_public_url:
        return None

    redirect_uri = f"{settings.backend_public_url}/integrations/mercado_livre/callback"
    params = {
        "response_type": "code",
        "client_id": settings.mercadolivre_client_id,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> dict | None:
    """Retorna {"access_token": ..., "user_id": ...} ou None."""
    settings = get_settings()
    if not (settings.mercadolivre_client_id and settings.mercadolivre_client_secret and settings.backend_public_url):
        return None

    redirect_uri = f"{settings.backend_public_url}/integrations/mercado_livre/callback"
    payload = {
        "grant_type": "authorization_code",
        "client_id": settings.mercadolivre_client_id,
        "client_secret": settings.mercadolivre_client_secret,
        "code": code,
        "redirect_uri": redirect_uri,
    }
    try:
        response = httpx.post(_TOKEN_URL, data=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    data = response.json()
    access_token = data.get("access_token")
    user_id = data.get("user_id")
    if not access_token or not user_id:
        return None
    return {"access_token": access_token, "user_id": str(user_id)}


def fetch_order(access_token: str, order_id: str) -> dict | None:
    url = f"https://api.mercadolibre.com/orders/{order_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def map_order_payload(order: dict) -> list[dict]:
    order_id = str(order.get("id"))
    date_created = order.get("date_created")
    order_date = date_created.split("T")[0] if date_created else None
    buyer = order.get("buyer") or {}
    customer_id = str(buyer["id"]) if buyer.get("id") else None

    rows = []
    for entry in order.get("order_items", []):
        item = entry.get("item") or {}
        quantity = entry.get("quantity")
        unit_price = entry.get("unit_price")
        if quantity is None or unit_price is None:
            continue
        rows.append(
            {
                "data_pedido": order_date,
                "pedido_id": order_id,
                "produto": item.get("title") or "Produto sem nome",
                "sku": item.get("seller_sku") or None,
                "categoria": None,
                "quantidade": quantity,
                "valor_unitario": unit_price,
                "valor_total": None,
                "cliente_id": customer_id,
                "custo_unitario": None,
            }
        )
    return rows
