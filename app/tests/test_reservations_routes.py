from app.database.connection import get_connection

"""Testes rota reservations com método POST"""

# Testa rota com requisição bem sucedida e com cleanup de registro
def test_create_reservation_success(user_tokens, create_fake_destination):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        client = user_tokens.get("client")
        access_token = user_tokens.get("access_token")

        create_response = client.post("/api/reservations", json={
            "destination_id" : create_fake_destination.get("fake_destination_id"),
            "travel_date" : "2030-01-01"
        },
        headers={
            "Authorization" : "Bearer {}".format(access_token)
        })

        assert create_response is not None
        assert create_response.status_code == 201
        assert create_response.json["success"] is True
        assert create_response.json["reservation_id"] != None

    finally:
        if cursor:
            cursor.execute("DELETE FROM reservations WHERE id = %s", (create_response.json["reservation_id"], ))

            if conn:
                conn.commit()
                cursor.close()
                conn.close()

# Testa rota sem identidade do token
def test_create_reservation_none_identity(user_tokens, create_fake_destination, mock_none_identity_token):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={
        "destination_id" : create_fake_destination.get("fake_destination_id"),
        "travel_date" : "2030-01-01"
    },
    headers={
        "Authorization" : "Bearer {}".format(access_token)
    })

    assert response is not None
    assert response.status_code == 401
    assert response.json["success"] is False
    assert response.json["message"] == "Usuário não existe ou não está autorizado"

# Testa rota com JSON inválido
def test_create_reservation_invalid_json(user_tokens):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={}, headers={"Authorization" : "Bearer {}".format(access_token)})
    
    assert response is not None
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "JSON inválido"

# Testa rota com id de destino inexistente/inválido
def test_create_reservations_none_destination(user_tokens):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={
        "destination_id" : 1,
        "travel_date" : "2030-01-01"
    },
    headers={
        "Authorization" : "Bearer {}".format(access_token)
    })

    assert response is not None
    assert response.status_code == 404
    assert response.json["success"] is False
    assert response.json["message"] == "Destino não disponível ou não encontrado."

# Testa rota com formato de data inválido
def test_create_reservation_date_format(user_tokens, create_fake_destination):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={
        "destination_id" : create_fake_destination.get("fake_destination_id"),
        "travel_date" : "01/01/2030"
    },
    headers={
        "Authorization" : "Bearer {}".format(access_token)
    })

    assert response is not None
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Formato de data inválido (dd/mm/aaaa)."

# Testa rota com data passada
def test_create_reservation_past_date(user_tokens, create_fake_destination):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={
        "destination_id" : create_fake_destination.get("fake_destination_id"),
        "travel_date" : "2000-01-01"
    },
    headers={
        "Authorization" : "Bearer {}".format(access_token)
    })

    assert response is not None
    assert response.status_code == 400
    assert response.json["success"] is False
    assert response.json["message"] == "Data inválida. São aceitas somente datas posteriores à data de hoje."

# Testa falha na criação da reserva
def test_create_reservation_failed(user_tokens, create_fake_destination, mock_create_reservation_none):

    client = user_tokens.get("client")
    access_token = user_tokens.get("access_token")

    response = client.post("/api/reservations", json={
        "destination_id" : create_fake_destination.get("fake_destination_id"),
        "travel_date" : "2030-01-01"
    },
    headers={
        "Authorization" : "Bearer {}".format(access_token)
    })

    assert response is not None
    assert response.status_code == 500
    assert response.json["success"] is False
    assert response.json["message"] == "Não foi possível criar a reserva."