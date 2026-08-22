from datetime import datetime

from api_client import api_client
from config import settings
from mcp.server.mcpserver import Context, MCPServer

mcp = MCPServer("friends-activity-planner")


def _raise_for_status(response) -> None:
    if response.status_code >= 400:
        raise RuntimeError(f"API error {response.status_code}: {response.text}")


def _without_none(**fields) -> dict:
    return {k: v for k, v in fields.items() if v is not None}


def _token(ctx: Context) -> str:
    headers = ctx.headers or {}
    auth = headers.get("authorization") or headers.get("Authorization")
    if not auth:
        raise RuntimeError("Missing Authorization header on MCP request")
    return auth


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_activities(ctx: Context) -> list[dict]:
    """List all activities."""
    response = await api_client.request("GET", "/activities", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def get_activity(activity_id: int, ctx: Context) -> dict:
    """Get a single activity by id."""
    response = await api_client.request("GET", f"/activities/{activity_id}", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def create_activity(name: str, ctx: Context, description: str | None = None) -> dict:
    """Create a new activity."""
    response = await api_client.request(
        "POST", "/activities", token=_token(ctx), json=_without_none(name=name, description=description)
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def update_activity(
    activity_id: int, ctx: Context, name: str | None = None, description: str | None = None
) -> dict:
    """Update an activity. Only the provided fields are changed."""
    response = await api_client.request(
        "PATCH",
        f"/activities/{activity_id}",
        token=_token(ctx),
        json=_without_none(name=name, description=description),
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def delete_activity(activity_id: int, ctx: Context) -> str:
    """Delete an activity."""
    response = await api_client.request("DELETE", f"/activities/{activity_id}", token=_token(ctx))
    _raise_for_status(response)
    return f"Activity {activity_id} deleted"


# ---------------------------------------------------------------------------
# Schedules
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_schedules(ctx: Context) -> list[dict]:
    """List all schedules."""
    response = await api_client.request("GET", "/schedules", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def get_schedule(schedule_id: int, ctx: Context) -> dict:
    """Get a single schedule by id."""
    response = await api_client.request("GET", f"/schedules/{schedule_id}", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def create_schedule(start_date: datetime, end_date: datetime, ctx: Context) -> dict:
    """Create a new schedule with a start and end date (ISO 8601)."""
    response = await api_client.request(
        "POST",
        "/schedules",
        token=_token(ctx),
        json={"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def update_schedule(
    schedule_id: int, ctx: Context, start_date: datetime | None = None, end_date: datetime | None = None
) -> dict:
    """Update a schedule. Only the provided fields are changed."""
    payload = _without_none(
        start_date=start_date.isoformat() if start_date else None,
        end_date=end_date.isoformat() if end_date else None,
    )
    response = await api_client.request("PATCH", f"/schedules/{schedule_id}", token=_token(ctx), json=payload)
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def delete_schedule(schedule_id: int, ctx: Context) -> str:
    """Delete a schedule."""
    response = await api_client.request("DELETE", f"/schedules/{schedule_id}", token=_token(ctx))
    _raise_for_status(response)
    return f"Schedule {schedule_id} deleted"


# ---------------------------------------------------------------------------
# Opinions
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_opinions(ctx: Context) -> list[dict]:
    """List the current user's opinions about activities."""
    response = await api_client.request("GET", "/opinions", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def get_opinion(opinion_id: int, ctx: Context) -> dict:
    """Get a single opinion by id."""
    response = await api_client.request("GET", f"/opinions/{opinion_id}", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def create_opinion(
    name: str, activity_id: int, sentiment: int, ctx: Context, description: str | None = None
) -> dict:
    """Create an opinion about an activity. sentiment is 1-5: 1=strongly_dislike, 2=dislike,
    3=indifferent, 4=like, 5=strongly_like."""
    response = await api_client.request(
        "POST",
        "/opinions",
        token=_token(ctx),
        json=_without_none(name=name, activity_id=activity_id, sentiment=sentiment, description=description),
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def update_opinion(
    opinion_id: int,
    ctx: Context,
    name: str | None = None,
    activity_id: int | None = None,
    sentiment: int | None = None,
    description: str | None = None,
) -> dict:
    """Update an opinion. Only the provided fields are changed. sentiment is 1-5: 1=strongly_dislike,
    2=dislike, 3=indifferent, 4=like, 5=strongly_like."""
    payload = _without_none(name=name, activity_id=activity_id, sentiment=sentiment, description=description)
    response = await api_client.request("PATCH", f"/opinions/{opinion_id}", token=_token(ctx), json=payload)
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def delete_opinion(opinion_id: int, ctx: Context) -> str:
    """Delete an opinion."""
    response = await api_client.request("DELETE", f"/opinions/{opinion_id}", token=_token(ctx))
    _raise_for_status(response)
    return f"Opinion {opinion_id} deleted"


# ---------------------------------------------------------------------------
# Meets
# ---------------------------------------------------------------------------


@mcp.tool()
async def list_meets(ctx: Context) -> list[dict]:
    """List all meets."""
    response = await api_client.request("GET", "/meets", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def get_meet(meet_id: int, ctx: Context) -> dict:
    """Get a single meet by id."""
    response = await api_client.request("GET", f"/meets/{meet_id}", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def create_meet(schedule_id: int, meet_group_id: int, ctx: Context) -> dict:
    """Create a meet linking a schedule to a meet group."""
    response = await api_client.request(
        "POST",
        "/meets",
        token=_token(ctx),
        json={"schedule_id": schedule_id, "meet_group_id": meet_group_id},
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def update_meet(
    meet_id: int, ctx: Context, schedule_id: int | None = None, meet_group_id: int | None = None
) -> dict:
    """Update a meet. Only the provided fields are changed."""
    payload = _without_none(schedule_id=schedule_id, meet_group_id=meet_group_id)
    response = await api_client.request("PATCH", f"/meets/{meet_id}", token=_token(ctx), json=payload)
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def delete_meet(meet_id: int, ctx: Context) -> str:
    """Delete a meet."""
    response = await api_client.request("DELETE", f"/meets/{meet_id}", token=_token(ctx))
    _raise_for_status(response)
    return f"Meet {meet_id} deleted"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@mcp.tool()
async def find_user_by_email(email: str, ctx: Context) -> dict:
    """Look up a user by their exact email address. Use this to find a user's id
    before sending them a friend request."""
    response = await api_client.request("GET", "/users/lookup", token=_token(ctx), params={"email": email})
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def search_users_by_name(query: str, ctx: Context) -> list[dict]:
    """Search for users whose first or last name contains the given text (case-insensitive).
    Use this to find a friend's user id when you only know their name, not their email.
    May return multiple matches if several users share a similar name."""
    response = await api_client.request("GET", "/users/search", token=_token(ctx), params={"q": query})
    _raise_for_status(response)
    return response.json()


# ---------------------------------------------------------------------------
# Friends
# ---------------------------------------------------------------------------


@mcp.tool()
async def send_friend_request(to_user_id: int, ctx: Context) -> dict:
    """Send a friend request to another user by their user id."""
    response = await api_client.request(
        "POST", "/friends/requests", token=_token(ctx), json={"to_user_id": to_user_id}
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def list_incoming_friend_requests(ctx: Context) -> list[dict]:
    """List pending friend requests sent to the current user."""
    response = await api_client.request("GET", "/friends/requests", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def accept_friend_request(invitation_id: int, ctx: Context) -> dict:
    """Accept a pending friend request. The two users become mutual friends."""
    response = await api_client.request(
        "POST", f"/friends/requests/{invitation_id}/accept", token=_token(ctx)
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def reject_friend_request(invitation_id: int, ctx: Context) -> dict:
    """Reject a pending friend request."""
    response = await api_client.request(
        "POST", f"/friends/requests/{invitation_id}/reject", token=_token(ctx)
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def list_friends(ctx: Context) -> list[dict]:
    """List the current user's friends."""
    response = await api_client.request("GET", "/friends", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def list_friends_interested_in_activity(activity_id: int, ctx: Context) -> list[dict]:
    """List the current user's friends who have a positive opinion (like or strongly
    like) about the given activity. Use this before organizing a meetup for an
    activity, to suggest which friends might want to join."""
    response = await api_client.request(
        "GET", "/friends/interested", token=_token(ctx), params={"activity_id": activity_id}
    )
    _raise_for_status(response)
    return response.json()


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------


@mcp.tool()
async def create_group(name: str, ctx: Context) -> dict:
    """Create a new meet group (a named set of people who can attend a meet)."""
    response = await api_client.request("POST", "/groups", token=_token(ctx), json={"name": name})
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def list_groups(ctx: Context) -> list[dict]:
    """List all meet groups."""
    response = await api_client.request("GET", "/groups", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def add_group_member(group_id: int, user_id: int, ctx: Context) -> dict:
    """Add a user to a meet group by their user id."""
    response = await api_client.request(
        "POST", f"/groups/{group_id}/members", token=_token(ctx), json={"user_id": user_id}
    )
    _raise_for_status(response)
    return response.json()


@mcp.tool()
async def list_group_members(group_id: int, ctx: Context) -> list[dict]:
    """List the members of a meet group."""
    response = await api_client.request("GET", f"/groups/{group_id}/members", token=_token(ctx))
    _raise_for_status(response)
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)
