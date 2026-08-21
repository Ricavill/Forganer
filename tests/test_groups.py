def test_create_group_and_add_member(client, auth_headers):
    headers = auth_headers("group1@test.com")
    user_id = client.get("/users/lookup", params={"email": "group1@test.com"}, headers=headers).json()["id"]

    response = client.post("/groups", json={"name": "Weekend Crew"}, headers=headers)
    assert response.status_code == 201
    group_id = response.json()["id"]

    response = client.post(f"/groups/{group_id}/members", json={"user_id": user_id}, headers=headers)
    assert response.status_code == 201

    response = client.get(f"/groups/{group_id}/members", headers=headers)
    assert response.status_code == 200
    assert any(m["user_id"] == user_id for m in response.json())


def test_add_member_invalid_user_rejected(client, auth_headers):
    headers = auth_headers("group2@test.com")
    group_id = client.post("/groups", json={"name": "Group2"}, headers=headers).json()["id"]

    response = client.post(f"/groups/{group_id}/members", json={"user_id": 999999}, headers=headers)
    assert response.status_code == 400


def test_get_missing_group_404(client, auth_headers):
    headers = auth_headers("group3@test.com")
    response = client.get("/groups/999999", headers=headers)
    assert response.status_code == 404


def test_list_groups(client, auth_headers):
    headers = auth_headers("group4@test.com")
    client.post("/groups", json={"name": "Trivia Squad"}, headers=headers)

    response = client.get("/groups", headers=headers)
    assert response.status_code == 200
    assert any(g["name"] == "Trivia Squad" for g in response.json())
