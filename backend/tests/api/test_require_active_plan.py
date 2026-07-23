from io import BytesIO


def test_upload_blocked_with_pending_plan(api_client, client_record, db_session):
    client_record.plan_status = "pending"
    db_session.commit()

    csv_content = "data_pedido,pedido_id,produto,quantidade,valor_unitario\n2026-07-01,P1,Produto A,1,100\n"
    files = {"file": ("vendas.csv", BytesIO(csv_content.encode("utf-8")), "text/csv")}

    response = api_client.post("/data-sources/upload", files=files)

    assert response.status_code == 402


def test_integrations_authorize_blocked_with_pending_plan(api_client, client_record, db_session):
    client_record.plan_status = "pending"
    db_session.commit()

    response = api_client.get("/integrations/mercado_livre/authorize")

    assert response.status_code == 402


def test_report_still_accessible_with_pending_plan(api_client, client_record, db_session):
    client_record.plan_status = "pending"
    db_session.commit()

    response = api_client.get("/report")

    assert response.status_code == 200
