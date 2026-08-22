from datetime import datetime, timezone

from app.core.calendar import build_ics_invite


def test_build_ics_invite_contains_required_fields():
    ics = build_ics_invite(
        uid="meet-1@friends-activity-planner",
        summary="Board Games Night",
        description="Meetup organized via Friends Activity Planner: Board Games Night",
        start=datetime(2026, 9, 1, 18, 0, tzinfo=timezone.utc),
        end=datetime(2026, 9, 1, 20, 0, tzinfo=timezone.utc),
        organizer_email="organizer@test.com",
        attendee_emails=["a@test.com", "b@test.com"],
    )

    assert "BEGIN:VCALENDAR" in ics
    assert "METHOD:REQUEST" in ics
    assert "UID:meet-1@friends-activity-planner" in ics
    assert "DTSTART:20260901T180000Z" in ics
    assert "DTEND:20260901T200000Z" in ics
    assert "SUMMARY:Board Games Night" in ics
    assert "ORGANIZER:mailto:organizer@test.com" in ics
    attendee_prefix = "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE"
    assert f"{attendee_prefix}:mailto:a@test.com" in ics
    assert f"{attendee_prefix}:mailto:b@test.com" in ics
    assert ics.endswith("END:VCALENDAR\r\n")


def test_build_ics_invite_escapes_special_characters():
    ics = build_ics_invite(
        uid="meet-2@friends-activity-planner",
        summary="Board Games, Pizza; Fun",
        description="line one\nline two",
        start=datetime(2026, 9, 1, 18, 0, tzinfo=timezone.utc),
        end=datetime(2026, 9, 1, 20, 0, tzinfo=timezone.utc),
        organizer_email="organizer@test.com",
        attendee_emails=["a@test.com"],
    )

    assert "SUMMARY:Board Games\\, Pizza\\; Fun" in ics
    assert "DESCRIPTION:line one\\nline two" in ics
