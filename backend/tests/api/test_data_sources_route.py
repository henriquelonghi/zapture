from io import BytesIO


def test_upload_valid_csv_creates_orders(api_client):
    csv_content = "data_pedido,pedido_id,produto,quantidade,valor_unitario\n2026-07-01,P1,Produto A,1,100\n"
    files = {"file": ("vendas.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")}

    response = api_client.post("/data-sources/upload", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["orders_created"] == 1
    assert body["items_created"] == 1


def test_upload_missing_required_column_returns_422(api_client):
    csv_content = "produto,quantidade,valor_unitario\nProduto A,1,100\n"
    files = {"file": ("vendas.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")}

    response = api_client.post("/data-sources/upload", files=files)

    assert response.status_code == 422


def test_list_data_sources_reflects_last_upload(api_client):
    csv_content = "data_pedido,pedido_id,produto,quantidade,valor_unitario\n2026-07-01,P1,Produto A,1,100\n"
    files = {"file": ("vendas.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")}
    api_client.post("/data-sources/upload", files=files)

    response = api_client.get("/data-sources")

    assert response.status_code == 200
    sources = response.json()
    assert len(sources) == 1
    assert sources[0]["source_type"] == "upload"
    assert sources[0]["last_synced_at"] is not None


def test_sheets_connect_without_credentials_returns_500(api_client):
    response = api_client.post(
        "/data-sources/sheets/connect", json={"spreadsheet_id": "abc123", "range_name": "A1:Z100"}
    )

    assert response.status_code == 500
