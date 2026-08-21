def test_create_and_get_activity(client, auth_headers):
    headers = auth_headers("act1@test.com")

    response = client.post(
        "/activities", json={"name": "Chess Night", "description": "Weekly chess"}, headers=headers
    )
    assert response.status_code == 201
    activity_id = response.json()["id"]

    response = client.get(f"/activities/{activity_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Chess Night"


def test_list_activities(client, auth_headers):
    headers = auth_headers("act2@test.com")
    client.post("/activities", json={"name": "Bowling Night"}, headers=headers)

    response = client.get("/activities", headers=headers)
    assert response.status_code == 200
    assert any(a["name"] == "Bowling Night" for a in response.json())


def test_update_activity(client, auth_headers):
    headers = auth_headers("act3@test.com")
    activity_id = client.post("/activities", json={"name": "Board Games Night"}, headers=headers).json()["id"]

    response = client.patch(f"/activities/{activity_id}", json={"description": "Updated"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["description"] == "Updated"


def test_delete_activity_then_404(client, auth_headers):
    headers = auth_headers("act4@test.com")
    activity_id = client.post("/activities", json={"name": "Karaoke Session"}, headers=headers).json()["id"]

    response = client.delete(f"/activities/{activity_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/activities/{activity_id}", headers=headers)
    assert response.status_code == 404


def test_get_missing_activity_404(client, auth_headers):
    headers = auth_headers("act5@test.com")
    response = client.get("/activities/999999", headers=headers)
    assert response.status_code == 404


def test_activities_require_auth(client):
    response = client.get("/activities")
    assert response.status_code == 401


def test_create_similar_activity_rejected(client, auth_headers):
    headers = auth_headers("act6@test.com")

    first = client.post("/activities", json={"name": "Movie Night Marathon"}, headers=headers)
    assert first.status_code == 201

    duplicate = client.post("/activities", json={"name": "movie night marathon"}, headers=headers)
    assert duplicate.status_code == 400
    assert "similar" in duplicate.json()["detail"].lower()


def test_search_activities_finds_substring_match(client, auth_headers):
    headers = auth_headers("act7@test.com")
    client.post("/activities", json={"name": "Ultimate Frisbee League"}, headers=headers)

    response = client.get("/activities/search", params={"q": "frisbee"}, headers=headers)
    assert response.status_code == 200
    names = [a["name"] for a in response.json()]
    assert "Ultimate Frisbee League" in names
