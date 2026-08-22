from unittest.mock import MagicMock, patch

from app.core import email
from app.features.groups.models import MeetGroup, MeetGroupUser


def _create_group(db_session, name="Weekend Crew") -> int:
    group = MeetGroup(name=name)
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group.id


def _create_schedule(client, headers, start, end):
    return client.post("/schedules", json={"start_date": start, "end_date": end}, headers=headers).json()[
        "id"
    ]


def test_create_meet(client, auth_headers, db_session):
    headers = auth_headers("meet1@test.com")
    schedule_id = _create_schedule(client, headers, "2026-09-10T10:00:00Z", "2026-09-10T12:00:00Z")
    group_id = _create_group(db_session)

    response = client.post(
        "/meets", json={"schedule_id": schedule_id, "meet_group_id": group_id}, headers=headers
    )
    assert response.status_code == 201


def test_create_meet_invalid_schedule_rejected(client, auth_headers, db_session):
    headers = auth_headers("meet2@test.com")
    group_id = _create_group(db_session, "Group2")

    response = client.post("/meets", json={"schedule_id": 999999, "meet_group_id": group_id}, headers=headers)
    assert response.status_code == 400


def test_second_meet_on_overlapping_schedule_rejected(client, auth_headers, db_session):
    headers = auth_headers("meet3@test.com")
    schedule_id = _create_schedule(client, headers, "2026-09-11T10:00:00Z", "2026-09-11T12:00:00Z")
    group_a = _create_group(db_session, "GroupA")
    group_b = _create_group(db_session, "GroupB")

    first = client.post(
        "/meets", json={"schedule_id": schedule_id, "meet_group_id": group_a}, headers=headers
    )
    assert first.status_code == 201

    second = client.post(
        "/meets", json={"schedule_id": schedule_id, "meet_group_id": group_b}, headers=headers
    )
    assert second.status_code == 400


def test_delete_meet_then_404(client, auth_headers, db_session):
    headers = auth_headers("meet4@test.com")
    schedule_id = _create_schedule(client, headers, "2026-09-12T10:00:00Z", "2026-09-12T12:00:00Z")
    group_id = _create_group(db_session, "GroupC")

    meet_id = client.post(
        "/meets", json={"schedule_id": schedule_id, "meet_group_id": group_id}, headers=headers
    ).json()["id"]

    response = client.delete(f"/meets/{meet_id}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/meets/{meet_id}", headers=headers)
    assert response.status_code == 404


def test_send_invites_emails_all_group_members(client, auth_headers, db_session):
    headers = auth_headers("meet5@test.com")
    other_headers = auth_headers("meet5b@test.com")
    schedule_id = _create_schedule(client, headers, "2026-09-13T10:00:00Z", "2026-09-13T12:00:00Z")
    group_id = _create_group(db_session, "GroupD")

    organizer_id = client.get("/users/lookup", params={"email": "meet5@test.com"}, headers=headers).json()[
        "id"
    ]
    other_id = client.get("/users/lookup", params={"email": "meet5b@test.com"}, headers=other_headers).json()[
        "id"
    ]
    db_session.add(MeetGroupUser(user_id=organizer_id, meet_group_id=group_id))
    db_session.add(MeetGroupUser(user_id=other_id, meet_group_id=group_id))
    db_session.commit()

    meet_id = client.post(
        "/meets", json={"schedule_id": schedule_id, "meet_group_id": group_id}, headers=headers
    ).json()["id"]

    with patch.object(email, "send_email", MagicMock()) as mocked_send:
        response = client.post(f"/meets/{meet_id}/invite", headers=headers)

    assert response.status_code == 200
    sent_to = set(response.json()["sent_to"])
    assert sent_to == {"meet5@test.com", "meet5b@test.com"}

    mocked_send.assert_called_once()
    kwargs = mocked_send.call_args.kwargs
    assert set(kwargs["to"]) == sent_to
    assert kwargs["attachments"][0]["filename"] == "invite.ics"


def test_send_invites_missing_meet_404(client, auth_headers):
    headers = auth_headers("meet6@test.com")
    response = client.post("/meets/999999/invite", headers=headers)
    assert response.status_code == 404
