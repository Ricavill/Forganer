def _lookup_id(client, headers, email):
    return client.get("/users/lookup", params={"email": email}, headers=headers).json()["id"]


def test_send_and_accept_friend_request_creates_mutual_friendship(client, auth_headers):
    headers_a = auth_headers("friend1a@test.com")
    headers_b = auth_headers("friend1b@test.com")
    bob_id = _lookup_id(client, headers_a, "friend1b@test.com")

    response = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a)
    assert response.status_code == 201
    invitation_id = response.json()["id"]

    response = client.get("/friends/requests", headers=headers_b)
    assert response.status_code == 200
    assert any(r["id"] == invitation_id for r in response.json())

    response = client.post(f"/friends/requests/{invitation_id}/accept", headers=headers_b)
    assert response.status_code == 200
    assert response.json()["status"] == 2

    assert len(client.get("/friends", headers=headers_a).json()) == 1
    assert len(client.get("/friends", headers=headers_b).json()) == 1


def test_reject_friend_request(client, auth_headers):
    headers_a = auth_headers("friend2a@test.com")
    headers_b = auth_headers("friend2b@test.com")
    bob_id = _lookup_id(client, headers_a, "friend2b@test.com")

    invitation_id = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a).json()[
        "id"
    ]

    response = client.post(f"/friends/requests/{invitation_id}/reject", headers=headers_b)
    assert response.status_code == 200
    assert response.json()["status"] == 3

    assert client.get("/friends", headers=headers_a).json() == []


def test_cannot_friend_request_self(client, auth_headers):
    headers = auth_headers("friend3@test.com")
    my_id = _lookup_id(client, headers, "friend3@test.com")

    response = client.post("/friends/requests", json={"to_user_id": my_id}, headers=headers)
    assert response.status_code == 422


def test_duplicate_pending_request_rejected(client, auth_headers):
    headers_a = auth_headers("friend4a@test.com")
    auth_headers("friend4b@test.com")
    bob_id = _lookup_id(client, headers_a, "friend4b@test.com")

    first = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a)
    assert first.status_code == 201

    second = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a)
    assert second.status_code == 400


def test_accept_wrong_recipient_rejected(client, auth_headers):
    headers_a = auth_headers("friend5a@test.com")
    auth_headers("friend5b@test.com")
    headers_c = auth_headers("friend5c@test.com")
    bob_id = _lookup_id(client, headers_a, "friend5b@test.com")

    invitation_id = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a).json()[
        "id"
    ]

    response = client.post(f"/friends/requests/{invitation_id}/accept", headers=headers_c)
    assert response.status_code == 404


def test_lookup_unknown_email_404(client, auth_headers):
    headers = auth_headers("friend6@test.com")
    response = client.get("/users/lookup", params={"email": "nobody@test.com"}, headers=headers)
    assert response.status_code == 404


def _befriend(client, headers_a, headers_b, email_b):
    bob_id = _lookup_id(client, headers_a, email_b)
    invitation_id = client.post("/friends/requests", json={"to_user_id": bob_id}, headers=headers_a).json()[
        "id"
    ]
    client.post(f"/friends/requests/{invitation_id}/accept", headers=headers_b)
    return bob_id


def test_interested_friends_surfaces_positive_opinion(client, auth_headers):
    headers_a = auth_headers("friend7a@test.com")
    headers_b = auth_headers("friend7b@test.com")
    bob_id = _befriend(client, headers_a, headers_b, "friend7b@test.com")

    activity_id = client.post("/activities", json={"name": "Rock Climbing"}, headers=headers_b).json()["id"]
    client.post(
        "/opinions",
        json={"name": "love it", "activity_id": activity_id, "sentiment": 5},
        headers=headers_b,
    )

    response = client.get("/friends/interested", params={"activity_id": activity_id}, headers=headers_a)
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["user_id"] == bob_id
    assert body[0]["sentiment"] == 5


def test_interested_friends_excludes_negative_opinion(client, auth_headers):
    headers_a = auth_headers("friend8a@test.com")
    headers_b = auth_headers("friend8b@test.com")
    _befriend(client, headers_a, headers_b, "friend8b@test.com")

    activity_id = client.post("/activities", json={"name": "Horror Movie Night"}, headers=headers_b).json()[
        "id"
    ]
    client.post(
        "/opinions",
        json={"name": "not for me", "activity_id": activity_id, "sentiment": 1},
        headers=headers_b,
    )

    response = client.get("/friends/interested", params={"activity_id": activity_id}, headers=headers_a)
    assert response.status_code == 200
    assert response.json() == []
