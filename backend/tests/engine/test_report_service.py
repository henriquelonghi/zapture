from datetime import date

from app.engine.report_service import generate_report
from app.ingestion.normalizer import normalize_and_persist


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


def test_generate_report_end_to_end(db_session, client):
    rows = [
        _row("P1", date(2026, 7, 10), "Produto A", 100, custo_unitario=40),
        _row("P2", date(2026, 6, 10), "Produto A", 80, custo_unitario=40),
    ]
    normalize_and_persist(db_session, client.id, rows)

    report = generate_report(db_session, client.id, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    assert report.revenue.total_current == 100
    assert report.revenue.total_previous == 80
    assert report.revenue.variation_pct == 25.0
    assert report.aggregate_margin.margin_pct == 60.0
    assert report.last_synced_at is None
    assert len(report.insights) >= 1


def test_generate_report_flags_negative_margin_as_insight(db_session, client):
    rows = [_row("P1", date(2026, 7, 10), "Produto Ruim", 100, custo_unitario=150)]
    normalize_and_persist(db_session, client.id, rows)

    report = generate_report(db_session, client.id, period_start=date(2026, 7, 1), period_end=date(2026, 7, 31))

    assert len(report.negative_margin_products) == 1
    assert any(i.category == "margem_negativa" for i in report.insights)
