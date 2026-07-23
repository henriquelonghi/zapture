from datetime import date

from app.ingestion.webhook_pipeline import ingest_order_rows
from app.models import DataSourceConnection, DataSourceType


def _row(pedido_id="P1", order_date=date(2026, 7, 10)):
    return {
        "data_pedido": order_date,
        "pedido_id": pedido_id,
        "produto": "Produto A",
        "sku": None,
        "categoria": None,
        "quantidade": 1,
        "valor_unitario": 100,
        "valor_total": 100,
        "cliente_id": None,
        "custo_unitario": None,
    }


def test_ingest_order_rows_creates_order_and_updates_sync_metadata_without_clobbering_config(db_session, client):
    connection = DataSourceConnection(
        client_id=client.id,
        source_type=DataSourceType.SHOPIFY,
        config={"access_token": "tok", "shop_domain": "loja.myshopify.com"},
    )
    db_session.add(connection)
    db_session.commit()

    outcome = ingest_order_rows(db_session, client.id, [_row()], DataSourceType.SHOPIFY, "Shopify")

    assert outcome.summary.orders_created == 1
    db_session.refresh(connection)
    assert connection.last_synced_at is not None
    assert connection.last_sync_label == "Shopify"
    assert connection.config == {"access_token": "tok", "shop_domain": "loja.myshopify.com"}


def test_ingest_order_rows_without_existing_connection_still_persists_order(db_session, client):
    outcome = ingest_order_rows(db_session, client.id, [_row()], DataSourceType.SHOPIFY, "Shopify")

    assert outcome.summary.orders_created == 1
    assert outcome.data_source is None


def test_ingest_order_rows_invalid_row_returns_invalid_outcome(db_session, client):
    bad_row = _row(pedido_id="")

    outcome = ingest_order_rows(db_session, client.id, [bad_row], DataSourceType.SHOPIFY, "Shopify")

    assert outcome.validation.is_valid is False
    assert outcome.summary is None
