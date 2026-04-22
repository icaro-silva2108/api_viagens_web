import pytest
from main import app
from app.database.connection import get_connection
from app.api.limiter import limiter
from unittest.mock import patch
import uuid

# Cria client que trata 'Too many requests[429]' durante os testes
@pytest.fixture(scope="function")
def client_no_ratelimit():

    previous_config = app.config["RATELIMIT_ENABLED"] = True
    app.config["RATELIMIT_ENABLED"] = False
    limiter.reset()

    try:
        yield app.test_client()
    finally:
        app.config["RATELIMIT_ENABLED"] = previous_config
        limiter.reset()

# Fixture de Rotas Protegidas
@pytest.fixture(scope="function", name="user_tokens")
def auth_fixture(client_no_ratelimit):
    conn = None
    cursor = None
    response_signup = None
    response_signin = None
    email = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        email = f"teste@{str(uuid.uuid4())}.com"

        client = client_no_ratelimit
        response_signup = client.post("/api/signup", json={
            "name" : "teste",
            "email" : email,
            "password" : "teste123",
            "password_confirm" : "teste123",
            "birth_date" : "2000-01-01"
        })

        response_signin = client.post("/api/signin", json={
            "email" : email,
            "password" : "teste123"
        })

        assert response_signup.status_code == 201
        assert response_signin.status_code == 200

        user_id = response_signin.json["user_id"]

        yield {
            "client" : client,
            "id" : response_signin.json["user_id"],
            "access_token" : response_signin.json["access_token"],
            "refresh_token" : response_signin.json["refresh_token"]
        }

    finally:
        if cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id, ))
            conn.commit()
            cursor.close()
        if conn:
            conn.close()

# Fixture sem cleanup para testar sucesso da rota DELETE profile
@pytest.fixture(scope="function", name="user_data_no_cleanup")
def auth_without_cleanup(client_no_ratelimit):

    email = f"teste@{str(uuid.uuid4())}.com"

    client = client_no_ratelimit
    response_signup = client.post("/api/signup", json={
        "name" : "teste",
        "email" : email,
        "password" : "teste123",
        "password_confirm" : "teste123",
        "birth_date" : "2000-01-01"
    })

    response_signin = client.post("/api/signin", json={
        "email" : email,
        "password" : "teste123"
    })

    assert response_signup.status_code == 201
    assert response_signin.status_code == 200

    user_id = response_signin.json["user_id"]

    yield {
        "client" : client,
        "user_id" : user_id,
        "refresh_token" : response_signin.json["refresh_token"]
    }

# Fixture de criação de destino para teste de criação de reservas
@pytest.fixture(scope="function")
def create_fake_destination():

    conn = None
    cursor = None
    fake_id = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if cursor:
            cursor.execute("""
                        INSERT INTO destinations
                        (city, country, description, price)
                        VALUES (%s, %s, %s, %s);""",
                        ("test_city", "test_country", "test_description", 1.00))
            if conn:
                conn.commit()
                fake_id = cursor.lastrowid
       
        yield{
            "fake_destination_id" : fake_id
        }

    finally:
        if cursor and fake_id:
            cursor.execute("DELETE FROM destinations WHERE id = %s;", (fake_id, ))

            if conn:
                conn.commit()
                cursor.close()
                conn.close()

# Fixture que cria reserva para teste de cancelamento
@pytest.fixture(scope="function")
def create_fake_reservation(user_tokens, create_fake_destination):

    conn = None
    cursor = None

    try:
        
        conn = get_connection()
        cursor = conn.cursor()

        if cursor:

            user_id = user_tokens.get("id")
            access_token = user_tokens.get("access_token")
            cursor.execute("""
                        INSERT INTO reservations
                        (user_id, destination_id, travel_date)
                        VALUES (%s, %s, %s);""",
                        (user_id, create_fake_destination.get("fake_destination_id"), "2040-12-30"))
        
            if conn:
                conn.commit()
                fake_id = cursor.lastrowid
        
        yield {
            "fake_reservation_id" : fake_id,
            "user_id" : user_id,
            "access_token" : access_token
        }

    finally:
        if cursor:
            cursor.close()

            if conn:
                conn.commit()
                conn.close()


"""Fixtures de Mocks para os testes"""

# Mock que força get_token_identity retornar None
@pytest.fixture(scope="function")
def mock_none_identity_token():

    with patch("app.api.protected_routes.get_token_identity", return_value=None):
        yield

# Mock que força search_user_reservation retornar True
@pytest.fixture(scope="function")
def mock_user_reservation_true():

    with patch("app.api.protected_routes.utilities.search_user_reservation", return_value=True):
        yield

# Mock que força delete_user retornar None
@pytest.fixture(scope="function")
def mock_delete_user_none():

    with patch("app.api.protected_routes.user_service.delete_user", return_value=None):
        yield

# Mock que força add_revoked_tokens retornar None
@pytest.fixture(scope="function")
def mock_add_revoked_tokens_none():

    with patch("app.api.protected_routes.utilities.add_revoked_tokens", return_value=None):
        yield

# Mock que força search_user_by_id retornar None
@pytest.fixture(scope="function")
def mock_search_user_by_id_none():

    with patch("app.api.protected_routes.utilities.search_user_by_id", return_value=None):
        yield

# Mock que força change_user_info retornar None
@pytest.fixture(scope="function")
def mock_change_user_info_none():

    with patch("app.api.protected_routes.user_service.change_user_info", return_value=None):
        yield

# Mock que força create_reservation retornar None
@pytest.fixture(scope="function")
def mock_create_reservation_none():

    with patch("app.api.protected_routes.reservation_service.create_reservation", return_value=None):
        yield

# Mock que cria side effect para levantar erro em send_access_token
@pytest.fixture(scope="function")
def mock_exception_access_token():

    with patch("app.api.protected_routes.send_access_token", side_effect=Exception("Erro simulado")):
        yield