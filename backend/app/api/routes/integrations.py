"""Rotas de conexão via OAuth (uma por plataforma) + recebimento de webhook
de pedidos. O fluxo authorize/callback usa `oauth_state` pra saber qual
client_id está se conectando (o callback é uma navegação de navegador vindo
da plataforma, sem o Bearer token do Supabase). O webhook não usa
autenticação de usuário — é verificado por assinatura/identificador da conta
conectada — e alimenta o motor via `webhook_pipeline`, que não sobrescreve o
`config` da conexão (é lá que mora o access_token)."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.core.config import get_settings
from app.ingestion.webhook_pipeline import ingest_order_rows
from app.integrations import mercado_livre, nuvemshop, oauth_state, shopify
from app.models import Client, DataSourceConnection, DataSourceType
from app.schemas.ingestion import AuthorizeUrlOut

router = APIRouter(tags=["integrations"])


def _get_or_create_connection(db: Session, client_id: uuid.UUID, source_type: DataSourceType) -> DataSourceConnection:
    connection = (
        db.query(DataSourceConnection)
        .filter(DataSourceConnection.client_id == client_id, DataSourceConnection.source_type == source_type)
        .first()
    )
    if connection is None:
        connection = DataSourceConnection(client_id=client_id, source_type=source_type, config={})
        db.add(connection)
    return connection


def _find_connection_by_config(
    db: Session, source_type: DataSourceType, key: str, value: str
) -> DataSourceConnection | None:
    """Sem índice JSON — número esperado de conexões é pequeno nesta fase do
    produto, então filtrar em Python evita depender de sintaxe de JSON path
    específica de Postgres (e quebrar nos testes, que rodam em SQLite)."""
    for candidate in db.query(DataSourceConnection).filter(DataSourceConnection.source_type == source_type).all():
        if (candidate.config or {}).get(key) == value:
            return candidate
    return None


def _redirect_to_frontend(path: str = "/relatorio") -> RedirectResponse:
    settings = get_settings()
    return RedirectResponse(url=f"{settings.frontend_origin}{path}")


# ---- Shopify ----


@router.get("/integrations/shopify/authorize", response_model=AuthorizeUrlOut)
def shopify_authorize(shop: str, client: Client = Depends(get_current_client)) -> AuthorizeUrlOut:
    state = oauth_state.create_state(client.id, "shopify")
    url = shopify.build_authorize_url(shop, state) if state else None
    if not url:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Integração com Shopify não configurada no servidor."
        )
    return AuthorizeUrlOut(authorize_url=url)


@router.get("/integrations/shopify/callback")
def shopify_callback(code: str, shop: str, state: str, db: Session = Depends(get_db)) -> RedirectResponse:
    client_id = oauth_state.decode_state(state, "shopify")
    if client_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "state inválido ou expirado.")

    access_token = shopify.exchange_code_for_token(shop, code)
    if not access_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Não foi possível trocar o código por um token de acesso.")

    connection = _get_or_create_connection(db, client_id, DataSourceType.SHOPIFY)
    connection.config = {"access_token": access_token, "shop_domain": shop}
    db.commit()

    return _redirect_to_frontend()


@router.post("/webhooks/shopify/orders")
async def shopify_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    raw_body = await request.body()
    hmac_header = request.headers.get("x-shopify-hmac-sha256")
    if not shopify.verify_webhook_hmac(raw_body, hmac_header):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Assinatura inválida.")

    shop = request.headers.get("x-shopify-shop-domain", "")
    connection = _find_connection_by_config(db, DataSourceType.SHOPIFY, "shop_domain", shop)
    if connection is None:
        return {"status": "ignored", "reason": "loja não conectada"}

    payload = await request.json()
    rows = shopify.map_order_payload(payload)
    ingest_order_rows(db, connection.client_id, rows, DataSourceType.SHOPIFY, "Shopify")
    return {"status": "ok"}


# ---- Mercado Livre ----


@router.get("/integrations/mercado_livre/authorize", response_model=AuthorizeUrlOut)
def mercado_livre_authorize(client: Client = Depends(get_current_client)) -> AuthorizeUrlOut:
    state = oauth_state.create_state(client.id, "mercado_livre")
    url = mercado_livre.build_authorize_url(state) if state else None
    if not url:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Integração com Mercado Livre não configurada no servidor."
        )
    return AuthorizeUrlOut(authorize_url=url)


@router.get("/integrations/mercado_livre/callback")
def mercado_livre_callback(code: str, state: str, db: Session = Depends(get_db)) -> RedirectResponse:
    client_id = oauth_state.decode_state(state, "mercado_livre")
    if client_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "state inválido ou expirado.")

    token_data = mercado_livre.exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Não foi possível trocar o código por um token de acesso.")

    connection = _get_or_create_connection(db, client_id, DataSourceType.MERCADO_LIVRE)
    connection.config = token_data
    db.commit()

    return _redirect_to_frontend()


@router.post("/webhooks/mercado_livre/orders")
async def mercado_livre_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.json()
    user_id = str(payload.get("user_id") or "")
    resource = payload.get("resource", "")
    order_id = resource.rsplit("/", 1)[-1] if resource else None
    if not user_id or not order_id:
        return {"status": "ignored", "reason": "payload sem user_id/resource"}

    connection = _find_connection_by_config(db, DataSourceType.MERCADO_LIVRE, "user_id", user_id)
    if connection is None:
        return {"status": "ignored", "reason": "conta não conectada"}

    order = mercado_livre.fetch_order(connection.config["access_token"], order_id)
    if order is None:
        return {"status": "error", "reason": "falha ao buscar pedido na API do Mercado Livre"}

    rows = mercado_livre.map_order_payload(order)
    ingest_order_rows(db, connection.client_id, rows, DataSourceType.MERCADO_LIVRE, "Mercado Livre")
    return {"status": "ok"}


# ---- Nuvemshop ----


@router.get("/integrations/nuvemshop/authorize", response_model=AuthorizeUrlOut)
def nuvemshop_authorize(client: Client = Depends(get_current_client)) -> AuthorizeUrlOut:
    state = oauth_state.create_state(client.id, "nuvemshop")
    url = nuvemshop.build_authorize_url(state) if state else None
    if not url:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Integração com Nuvemshop não configurada no servidor."
        )
    return AuthorizeUrlOut(authorize_url=url)


@router.get("/integrations/nuvemshop/callback")
def nuvemshop_callback(code: str, state: str, db: Session = Depends(get_db)) -> RedirectResponse:
    client_id = oauth_state.decode_state(state, "nuvemshop")
    if client_id is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "state inválido ou expirado.")

    token_data = nuvemshop.exchange_code_for_token(code)
    if not token_data:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Não foi possível trocar o código por um token de acesso.")

    connection = _get_or_create_connection(db, client_id, DataSourceType.NUVEMSHOP)
    connection.config = token_data
    db.commit()

    return _redirect_to_frontend()


@router.post("/webhooks/nuvemshop/orders")
async def nuvemshop_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    payload = await request.json()
    store_id = str(payload.get("store_id") or "")
    order_id = str(payload.get("id") or "")
    if not store_id or not order_id:
        return {"status": "ignored", "reason": "payload sem store_id/id"}

    connection = _find_connection_by_config(db, DataSourceType.NUVEMSHOP, "store_id", store_id)
    if connection is None:
        return {"status": "ignored", "reason": "loja não conectada"}

    order = nuvemshop.fetch_order(connection.config["access_token"], store_id, order_id)
    if order is None:
        return {"status": "error", "reason": "falha ao buscar pedido na API da Nuvemshop"}

    rows = nuvemshop.map_order_payload(order)
    ingest_order_rows(db, connection.client_id, rows, DataSourceType.NUVEMSHOP, "Nuvemshop")
    return {"status": "ok"}
