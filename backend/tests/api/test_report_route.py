from datetime import date

from fastapi.testclient import TestClient

from app.ingestion.normalizer import normalize_and_persist
from app.main import app


def _row(pedido_id, order_date, produto, valor_unitario):
    return {
        "data_pedido": order_date,
        "pedido_id": pedido_id,
        "produto": produto,
        "sku": None,
        "categoria": None,
        "quantidade": 1,
        "valor_unitario": valor_unitario,
        "valor_total": valor_unitario,
        "cliente_id": None,
        "custo_unitario": None,
    }


def test_get_report_returns_metrics_and_insights(api_client, db_session, client_record):
    normalize_and_persist(db_session, client_record.id, [_row("P1", date.today(), "Produto A", 100)])

    response = api_client.get("/report")

    assert response.status_code == 200
    body = response.json()
    assert body["revenue"]["total_current"] == 100
    assert "insights" in body
    assert body["last_synced_at"] is None


def test_get_report_requires_auth_without_override():
    with TestClient(app) as raw_client:
        response = raw_client.get("/report")

    assert response.status_code == 401
