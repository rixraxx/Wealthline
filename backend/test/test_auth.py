from fastapi.testclient import TestClient
from app.main import app

def test_register_user(client: TestClient):
    payload = {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate_email(client: TestClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "First User",
    }
    client.post("/api/v1/auth/register", json=payload)

    # Second attempt with same email
    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_login_success(client: TestClient):
    # Register user first
    email = "login_test@example.com"
    password = "MyPassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Login User"},
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user_me(client: TestClient):
    email = "metest@example.com"
    password = "MyPassword123"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Me User"},
    )

    login_res = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]

    me_res = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_login_rate_limit_exceeded(client):
    """Verify slowapi rate limiting triggers HTTP 429 after 5 rapid requests on /auth/login."""
    from app.main import app
    if hasattr(app.state, "limiter"):
        app.state.limiter.reset()

    login_payload = {
        "email": "ratelimit_test@example.com",
        "password": "WrongPassword123!",
    }

    # First 5 attempts should pass through (fail auth, but not rate limited)
    for _ in range(5):
        res = client.post("/api/v1/auth/login", json=login_payload)
        assert res.status_code != 429

    # The 6th request triggers rate limiting
    response = client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 429
