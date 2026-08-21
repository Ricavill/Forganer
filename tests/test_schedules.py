def _create_schedule(client, headers, start="2026-09-01T10:00:00Z", end="2026-09-01T12:00:00Z"):
    return client.post("/schedules", json={"start_date": start, "end_date": end}, headers=headers)


def test_create_schedule(client, auth_headers):
    headers = auth_headers("sched1@test.com")
    response = _create_schedule(client, headers)
    assert response.status_code == 201


def test_create_schedule_rejects_start_after_end(client, auth_headers):
    headers = auth_headers("sched2@test.com")
    response = _create_schedule(client, headers, start="2026-09-01T12:00:00Z", end="2026-09-01T10:00:00Z")
    assert response.status_code == 422


def test_create_schedule_rejects_equal_start_and_end(client, auth_headers):
    headers = auth_headers("sched3@test.com")
    response = _create_schedule(client, headers, start="2026-09-01T10:00:00Z", end="2026-09-01T10:00:00Z")
    assert response.status_code == 422


def test_create_overlapping_schedule_rejected(client, auth_headers):
    headers = auth_headers("sched4@test.com")
    _create_schedule(client, headers, start="2026-09-02T10:00:00Z", end="2026-09-02T12:00:00Z")

    response = _create_schedule(client, headers, start="2026-09-02T11:00:00Z", end="2026-09-02T13:00:00Z")
    assert response.status_code == 400


def test_create_adjacent_schedule_allowed(client, auth_headers):
    headers = auth_headers("sched5@test.com")
    _create_schedule(client, headers, start="2026-09-03T10:00:00Z", end="2026-09-03T12:00:00Z")

    response = _create_schedule(client, headers, start="2026-09-03T12:00:00Z", end="2026-09-03T13:00:00Z")
    assert response.status_code == 201


def test_update_schedule_to_overlap_rejected(client, auth_headers):
    headers = auth_headers("sched6@test.com")
    _create_schedule(client, headers, start="2026-09-04T10:00:00Z", end="2026-09-04T12:00:00Z")
    other_id = _create_schedule(
        client, headers, start="2026-09-04T12:00:00Z", end="2026-09-04T13:00:00Z"
    ).json()["id"]

    response = client.patch(
        f"/schedules/{other_id}", json={"start_date": "2026-09-04T11:00:00Z"}, headers=headers
    )
    assert response.status_code == 400


def test_delete_schedule_then_404(client, auth_headers):
    headers = auth_headers("sched7@test.com")
    schedule_id = _create_schedule(client, headers).json()["id"]

    response = client.delete(f"/schedules/{schedule_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/schedules/{schedule_id}", headers=headers)
    assert response.status_code == 404
