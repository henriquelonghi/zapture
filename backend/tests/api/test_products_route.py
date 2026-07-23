from app.models import Product


def test_list_products_returns_empty_when_none_exist(api_client):
    response = api_client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


def test_list_products_shows_null_cost_when_none_registered(api_client, db_session, client_record):
    product = Product(client_id=client_record.id, sku="SKU-A", name="Produto A", category="Categoria X")
    db_session.add(product)
    db_session.commit()

    response = api_client.get("/products")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["unit_cost"] is None
    assert body[0]["name"] == "Produto A"


def test_set_product_cost_creates_and_updates(api_client, db_session, client_record):
    product = Product(client_id=client_record.id, sku="SKU-A", name="Produto A")
    db_session.add(product)
    db_session.commit()

    response = api_client.put(f"/products/{product.id}/cost", json={"unit_cost": 42.5})
    assert response.status_code == 200
    assert response.json()["unit_cost"] == 42.5

    response = api_client.put(f"/products/{product.id}/cost", json={"unit_cost": 50.0})
    assert response.status_code == 200
    assert response.json()["unit_cost"] == 50.0

    list_response = api_client.get("/products")
    assert list_response.json()[0]["unit_cost"] == 50.0


def test_set_product_cost_rejects_negative_value(api_client, db_session, client_record):
    product = Product(client_id=client_record.id, sku="SKU-A", name="Produto A")
    db_session.add(product)
    db_session.commit()

    response = api_client.put(f"/products/{product.id}/cost", json={"unit_cost": -1})

    assert response.status_code == 400


def test_set_product_cost_for_unknown_product_returns_404(api_client):
    response = api_client.put(
        "/products/00000000-0000-0000-0000-000000000000/cost", json={"unit_cost": 10}
    )

    assert response.status_code == 404


def test_set_product_cost_scoped_to_client(api_client, db_session):
    from app.models import Client

    other_client = Client(name="Outra loja")
    db_session.add(other_client)
    db_session.commit()
    other_product = Product(client_id=other_client.id, sku="SKU-X", name="Produto de outro client")
    db_session.add(other_product)
    db_session.commit()

    response = api_client.put(f"/products/{other_product.id}/cost", json={"unit_cost": 10})

    assert response.status_code == 404
