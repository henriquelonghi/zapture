"""Integração com a Shopify Admin API: OAuth (app instalável na loja) +
webhook de pedidos. O payload do webhook já traz o pedido inteiro (line_items
incluídos) — diferente de Mercado Livre/Nuvemshop, não precisa de uma segunda
chamada pra buscar o recurso. Custo do produto não vem nesse payload (mora em
InventoryItem, um recurso separado); margem por produto continua dependendo
de cadastro manual mesmo com a integração ligada, igual documentado em
descricao.md §3."""

import base64
import hashlib
import hmac
from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

_AUTHORIZE_PATH = "/admin/oauth/authorize"
_TOKEN_PATH = "/admin/oauth/access_token"


def build_authorize_url(shop: str, state: str) -> str | None:
    settings = get_settings()
    if not settings.shopify_api_key or not settings.backend_public_url:
        return None

    redirect_uri = f"{settings.backend_public_url}/integrations/shopify/callback"
    params = {
        "client_id": settings.shopify_api_key,
        "scope": settings.shopify_scopes,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    return f"https://{shop}{_AUTHORIZE_PATH}?{urlencode(params)}"


def exchange_code_for_token(shop: str, code: str) -> str | None:
    settings = get_settings()
    if not settings.shopify_api_key or not settings.shopify_api_secret:
        return None

    url = f"https://{shop}{_TOKEN_PATH}"
    payload = {
        "client_id": settings.shopify_api_key,
        "client_secret": settings.shopify_api_secret,
        "code": code,
    }
    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json().get("access_token")


def verify_webhook_hmac(raw_body: bytes, hmac_header: str | None) -> bool:
    settings = get_settings()
    if not settings.shopify_api_secret or not hmac_header:
        return False

    digest = hmac.new(settings.shopify_api_secret.encode(), raw_body, hashlib.sha256).digest()
    computed = base64.b64encode(digest).decode()
    return hmac.compare_digest(computed, hmac_header)


def map_order_payload(payload: dict) -> list[dict]:
    order_id = str(payload.get("id"))
    created_at = payload.get("created_at")
    order_date = created_at.split("T")[0] if created_at else None
    customer = payload.get("customer") or {}
    customer_id = str(customer["id"]) if customer.get("id") else None

    rows = []
    for item in payload.get("line_items", []):
        quantity = item.get("quantity")
        unit_price = item.get("price")
        if quantity is None or unit_price is None:
            continue
        rows.append(
            {
                "data_pedido": order_date,
                "pedido_id": order_id,
                "produto": item.get("title") or item.get("name") or "Produto sem nome",
                "sku": item.get("sku") or None,
                "categoria": None,
                "quantidade": quantity,
                "valor_unitario": unit_price,
                "valor_total": None,
                "cliente_id": customer_id,
                "custo_unitario": None,
            }
        )
    return rows
