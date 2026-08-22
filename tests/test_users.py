def test_search_users_by_first_name(client, auth_headers):
    headers = auth_headers("search1@test.com")
    client.post(
        "/users/signup",
        json={"name": "Zelda", "last_name": "Zephyr", "email": "zelda1@test.com", "password": "secret123"},
    )

    response = client.get("/users/search", params={"q": "Zeld"}, headers=headers)
    assert response.status_code == 200
    assert any(u["email"] == "zelda1@test.com" for u in response.json())


def test_search_users_by_last_name(client, auth_headers):
    headers = auth_headers("search2@test.com")
    client.post(
        "/users/signup",
        json={
            "name": "Quinn",
            "last_name": "Quicksilver",
            "email": "quinn2@test.com",
            "password": "secret123",
        },
    )

    response = client.get("/users/search", params={"q": "Quicksil"}, headers=headers)
    assert response.status_code == 200
    assert any(u["email"] == "quinn2@test.com" for u in response.json())


def test_search_users_excludes_self(client, auth_headers):
    # auth_headers always signs up as name="Test", last_name="User"
    headers_a = auth_headers("search3a@test.com")
    auth_headers("search3b@test.com")

    response = client.get("/users/search", params={"q": "Test"}, headers=headers_a)
    assert response.status_code == 200
    emails = [u["email"] for u in response.json()]
    assert "search3a@test.com" not in emails
    assert "search3b@test.com" in emails


def test_search_users_no_match(client, auth_headers):
    headers = auth_headers("search4@test.com")
    response = client.get("/users/search", params={"q": "NoSuchPersonXYZ"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == []
