def _create_activity(client, headers, name="Reading Club"):
    return client.post("/activities", json={"name": name}, headers=headers).json()["id"]


def test_create_opinion(client, auth_headers):
    headers = auth_headers("op1@test.com")
    activity_id = _create_activity(client, headers)

    response = client.post(
        "/opinions",
        json={"name": "love it", "activity_id": activity_id, "sentiment": 5},
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["sentiment"] == 5


def test_create_opinion_invalid_sentiment_rejected(client, auth_headers):
    headers = auth_headers("op2@test.com")
    activity_id = _create_activity(client, headers, "Painting Class")

    response = client.post(
        "/opinions",
        json={"name": "meh", "activity_id": activity_id, "sentiment": 99},
        headers=headers,
    )
    assert response.status_code == 422


def test_create_opinion_invalid_activity_rejected(client, auth_headers):
    headers = auth_headers("op3@test.com")

    response = client.post(
        "/opinions",
        json={"name": "bad ref", "activity_id": 999999, "sentiment": 3},
        headers=headers,
    )
    assert response.status_code == 400


def test_update_opinion_sentiment(client, auth_headers):
    headers = auth_headers("op4@test.com")
    activity_id = _create_activity(client, headers, "Pottery Workshop")
    opinion_id = client.post(
        "/opinions",
        json={"name": "ok", "activity_id": activity_id, "sentiment": 3},
        headers=headers,
    ).json()["id"]

    response = client.patch(f"/opinions/{opinion_id}", json={"sentiment": 1}, headers=headers)
    assert response.status_code == 200
    assert response.json()["sentiment"] == 1


def test_delete_opinion_then_404(client, auth_headers):
    headers = auth_headers("op5@test.com")
    activity_id = _create_activity(client, headers, "Cycling Group")
    opinion_id = client.post(
        "/opinions",
        json={"name": "good", "activity_id": activity_id, "sentiment": 4},
        headers=headers,
    ).json()["id"]

    response = client.delete(f"/opinions/{opinion_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/opinions/{opinion_id}", headers=headers)
    assert response.status_code == 404


def test_opinions_are_scoped_per_user(client, auth_headers):
    headers_a = auth_headers("op6a@test.com")
    headers_b = auth_headers("op6b@test.com")
    activity_id = _create_activity(client, headers_a, "Trivia Night")

    opinion_id = client.post(
        "/opinions",
        json={"name": "mine", "activity_id": activity_id, "sentiment": 4},
        headers=headers_a,
    ).json()["id"]

    response = client.get(f"/opinions/{opinion_id}", headers=headers_b)
    assert response.status_code == 404

    response = client.get("/opinions", headers=headers_b)
    assert response.status_code == 200
    assert response.json() == []
