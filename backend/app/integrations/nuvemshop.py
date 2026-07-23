"""Integração com a API da Nuvemshop (Tiendanube): OAuth + webhook.

Assumido, pelo mesmo motivo do Mercado Livre, que o webhook manda só o
identificador do pedido e é preciso buscar o recurso completo via API — isso
precisa ser confirmado contra a documentação atual antes de ir pra produção;
se o payload já vier completo, o fetch abaixo vira redundante mas não incorreto.
O nome do header de assinatura do webhook e o suporte a `state` na URL de
autorização (o redirect_uri costuma ser fixo, configurado no painel do app,
não passado por query) também precisam da mesma checagem antes do primeiro
lançamento real."""

from urllib.parse import urlencode

import httpx

from app.core.config import get_settings

_AUTHORIZE_URL_TEMPLATE = "https://www.tiendanube.com/apps/{client_id}/authorize"
_TOKEN_URL = "https://www.tiendanube.com/apps/authorize/token"
_APP_USER_AGENT = "Zapture (contato@zapture.app)"


def build_authorize_url(state: str) -> str | None:
    settings = get_settings()
    if not settings.nuvemshop_client_id:
        return None

    base = _AUTHORIZE_URL_TEMPLATE.format(client_id=settings.nuvemshop_client_id)
    return f"{base}?{urlencode({'state': state})}"


def exchange_code_for_token(code: str) -> dict | None:
    """Retorna {"access_token": ..., "store_id": ...} ou None."""
    settings = get_settings()
    if not settings.nuvemshop_client_id or not settings.nuvemshop_client_secret:
        return None

    payload = {
        "client_id": settings.nuvemshop_client_id,
        "client_secret": settings.nuvemshop_client_secret,
        "grant_type": "authorization_code",
        "code": code,
    }
    try:
        response = httpx.post(_TOKEN_URL, json=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None

    data = response.json()
    access_token = data.get("access_token")
    store_id = data.get("user_id")
    if not access_token or not store_id:
        return None
    return {"access_token": access_token, "store_id": str(store_id)}


def fetch_order(access_token: str, store_id: str, order_id: str) -> dict | None:
    url = f"https://api.tiendanube.com/v1/{store_id}/orders/{order_id}"
    headers = {"Authentication": f"bearer {access_token}", "User-Agent": _APP_USER_AGENT}
    try:
        response = httpx.get(url, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def map_order_payload(order: dict) -> list[dict]:
    order_id = str(order.get("id"))
    created_at = order.get("created_at")
    order_date = created_at.split("T")[0] if created_at else None
    customer = order.get("customer") or {}
    customer_id = str(customer["id"]) if customer.get("id") else None

    rows = []
    for product in order.get("products", []):
        quantity = product.get("quantity")
        unit_price = product.get("price")
        if quantity is None or unit_price is None:
            continue
        rows.append(
            {
                "data_pedido": order_date,
                "pedido_id": order_id,
                "produto": product.get("name") or "Produto sem nome",
                "sku": product.get("sku") or None,
                "categoria": None,
                "quantidade": quantity,
                "valor_unitario": unit_price,
                "valor_total": None,
                "cliente_id": customer_id,
                "custo_unitario": None,
            }
        )
    return rows
