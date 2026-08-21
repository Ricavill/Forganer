def test_signup_returns_token(client):
    response = client.post(
        "/users/signup",
        json={"name": "A", "last_name": "B", "email": "signup@test.com", "password": "secret123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_signup_duplicate_email_rejected(client):
    payload = {"name": "A", "last_name": "B", "email": "dup@test.com", "password": "secret123"}
    first = client.post("/users/signup", json=payload)
    assert first.status_code == 201

    second = client.post("/users/signup", json={**payload, "password": "other456"})
    assert second.status_code == 400
    assert "already registered" in second.json()["detail"]


def test_signup_invalid_email_format_rejected(client):
    response = client.post(
        "/users/signup",
        json={"name": "A", "last_name": "B", "email": "not-an-email", "password": "secret123"},
    )
    assert response.status_code == 422


def test_login_success(client):
    payload = {"name": "A", "last_name": "B", "email": "login@test.com", "password": "secret123"}
    client.post("/users/signup", json=payload)

    response = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_wrong_password_rejected(client):
    payload = {"name": "A", "last_name": "B", "email": "login2@test.com", "password": "secret123"}
    client.post("/users/signup", json=payload)

    response = client.post("/auth/login", json={"email": payload["email"], "password": "wrong"})
    assert response.status_code == 401


def test_me_requires_auth(client):
    response = client.get("/auth/me")
    assert response.status_code == 403


def test_me_returns_current_user(client, auth_headers):
    headers = auth_headers("me@test.com")
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


def test_me_rejects_invalid_token(client):
    response = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
