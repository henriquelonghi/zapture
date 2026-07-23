from datetime import date

from app.ingestion.normalizer import normalize_and_persist
from app.models import Order


def _row(pedido_id, produto, sku=None, cliente_id=None, custo_unitario=None):
    return {
        "data_pedido": date(2026, 7, 1),
        "pedido_id": pedido_id,
        "produto": produto,
        "sku": sku,
        "categoria": None,
        "quantidade": 1,
        "valor_unitario": 10,
        "valor_total": 10,
        "cliente_id": cliente_id,
        "custo_unitario": custo_unitario,
    }


def test_normalize_creates_order_and_items(db_session, client):
    rows = [_row("P1", "Produto A", sku="SKU1"), _row("P1", "Produto B", sku="SKU2")]

    summary = normalize_and_persist(db_session, client.id, rows)

    assert summary.orders_created == 1
    assert summary.items_created == 2

    order = db_session.query(Order).filter(Order.client_id == client.id).one()
    assert len(order.items) == 2


def test_normalize_reingestion_replaces_items(db_session, client):
    normalize_and_persist(db_session, client.id, [_row("P1", "Produto A")])
    summary = normalize_and_persist(db_session, client.id, [_row("P1", "Produto A"), _row("P1", "Produto B")])

    assert summary.orders_updated == 1
    order = db_session.query(Order).filter(Order.client_id == client.id).one()
    assert len(order.items) == 2


def test_normalize_links_customer(db_session, client):
    normalize_and_persist(db_session, client.id, [_row("P1", "Produto A", cliente_id="cliente@teste.com")])

    order = db_session.query(Order).filter(Order.client_id == client.id).one()
    assert order.customer is not None
    assert order.customer.external_customer_id == "cliente@teste.com"


def test_normalize_reuses_manually_registered_cost_when_row_has_none(db_session, client):
    from app.models import Product, ProductCost

    product = Product(client_id=client.id, sku="SKU1", name="Produto A")
    db_session.add(product)
    db_session.flush()
    db_session.add(ProductCost(client_id=client.id, product_id=product.id, unit_cost=40))
    db_session.commit()

    normalize_and_persist(db_session, client.id, [_row("P1", "Produto A", sku="SKU1")])

    order = db_session.query(Order).filter(Order.client_id == client.id).one()
    assert float(order.items[0].unit_cost) == 40.0
