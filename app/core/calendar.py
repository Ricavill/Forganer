from datetime import datetime, timezone


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def _fmt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_ics_invite(
    *,
    uid: str,
    summary: str,
    description: str,
    start: datetime,
    end: datetime,
    organizer_email: str,
    attendee_emails: list[str],
) -> str:
    """A minimal RFC 5545 VCALENDAR with METHOD:REQUEST, so mail clients (including
    iOS Mail) recognize it as a calendar invite and offer to add it, with
    accept/decline for each attendee."""
    attendees = "\r\n".join(
        f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:mailto:{email}"
        for email in attendee_emails
    )

    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//Friends Activity Planner//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:REQUEST\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{_fmt(datetime.now(timezone.utc))}\r\n"
        f"DTSTART:{_fmt(start)}\r\n"
        f"DTEND:{_fmt(end)}\r\n"
        f"SUMMARY:{_escape(summary)}\r\n"
        f"DESCRIPTION:{_escape(description)}\r\n"
        f"ORGANIZER:mailto:{organizer_email}\r\n"
        f"{attendees}\r\n"
        "STATUS:CONFIRMED\r\n"
        "SEQUENCE:0\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
