def test_get_me_returns_client_info(api_client, client_record):
    response = api_client.get("/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(client_record.id)
    assert body["name"] == client_record.name
    assert body["whatsapp_phone"] is None


def test_update_me_sets_whatsapp_phone(api_client):
    response = api_client.patch("/me", json={"whatsapp_phone": "5511999998888"})

    assert response.status_code == 200
    assert response.json()["whatsapp_phone"] == "5511999998888"


def test_update_me_rejects_invalid_phone(api_client):
    response = api_client.patch("/me", json={"whatsapp_phone": "not-a-phone"})

    assert response.status_code == 400


def test_update_me_clears_phone_with_empty_string(api_client):
    api_client.patch("/me", json={"whatsapp_phone": "5511999998888"})

    response = api_client.patch("/me", json={"whatsapp_phone": ""})

    assert response.status_code == 200
    assert response.json()["whatsapp_phone"] is None
