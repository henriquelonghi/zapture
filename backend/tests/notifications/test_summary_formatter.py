from datetime import date

from app.engine.report_service import generate_report
from app.ingestion.normalizer import normalize_and_persist
from app.notifications.summary_formatter import format_summary_message


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


def test_format_summary_message_includes_headline_numbers(db_session, client):
    rows = [
        _row("P1", date(2026, 7, 10), "Produto A", 100, custo_unitario=40),
        _row("P2", date(2026, 6, 10), "Produto A", 80, custo_unitario=40),
    ]
    normalize_and_persist(db_session, client.id, rows)
    report = generate_report(db_session, client.id, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    message = format_summary_message(client.name, report)

    assert "Faturamento: R$ 100.00" in message
    assert "vs. período anterior" in message
    assert "1 pedidos" in message
    assert "Ticket médio" in message
    assert "Nenhuma fonte de dados conectada ainda." in message


def test_format_summary_message_includes_negative_margin_alert(db_session, client):
    rows = [_row("P1", date(2026, 7, 10), "Produto Ruim", 100, custo_unitario=150)]
    normalize_and_persist(db_session, client.id, rows)
    report = generate_report(db_session, client.id, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    message = format_summary_message(client.name, report)

    assert "⚠️" in message
    assert "Produto Ruim" in message
