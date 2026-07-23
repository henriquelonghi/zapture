from datetime import date

from app.ingestion.normalizer import normalize_and_persist
from app.notifications import summary_job


def _row(pedido_id, order_date, produto, valor_unitario, quantidade=1, custo_unitario=None, cliente_id=None):
    return {
        "data_pedido": order_date,
        "pedido_id": pedido_id,
        "produto": produto,
        "sku": None,
        "categoria": None,
        "quantidade": quantidade,
        "valor_unitario": valor_unitario,
        "valor_total": valor_unitario * quantidade,
        "cliente_id": cliente_id,
        "custo_unitario": custo_unitario,
    }


def test_send_periodic_summaries_sends_to_clients_with_phone(db_session, client, monkeypatch):
    client.whatsapp_phone = "5511999998888"
    db_session.commit()
    normalize_and_persist(db_session, client.id, [_row("P1", date(2026, 7, 10), "Produto A", 100)])

    sent_messages = []

    def fake_send(to_phone, message):
        sent_messages.append((to_phone, message))
        return True

    monkeypatch.setattr(summary_job, "send_whatsapp_message", fake_send)

    results = summary_job.send_periodic_summaries(db_session, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    assert len(results) == 1
    assert results[0].sent is True
    assert results[0].client_id == client.id
    assert sent_messages[0][0] == "5511999998888"


def test_send_periodic_summaries_skips_clients_without_phone(db_session, client):
    results = summary_job.send_periodic_summaries(db_session, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    assert results == []


def test_send_periodic_summaries_reports_failure_reason(db_session, client, monkeypatch):
    client.whatsapp_phone = "5511999998888"
    db_session.commit()
    normalize_and_persist(db_session, client.id, [_row("P1", date(2026, 7, 10), "Produto A", 100)])

    monkeypatch.setattr(summary_job, "send_whatsapp_message", lambda to_phone, message: False)

    results = summary_job.send_periodic_summaries(db_session, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    assert results[0].sent is False
    assert results[0].reason is not None
