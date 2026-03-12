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

@pytest.fixture(scope="function")
def mock_none_identity_token():

    with patch("app.api.protected_routes.get_token_identity", return_value=None):
        yield

@pytest.fixture(scope="function")
def mock_user_reservation_true():

    with patch("app.api.protected_routes.utilities.search_user_reservation", return_value=True):
        yield