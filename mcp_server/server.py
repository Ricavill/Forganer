from datetime import datetime

from mcp.server.mcpserver import Context, MCPServer

from api_client import api_client
from config import settings

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
    name: str, activity_id: int, sentiment: str, ctx: Context, description: str | None = None
) -> dict:
    """Create an opinion about an activity. sentiment must be one of: strongly_like, like,
    indifferent, dislike, strongly_dislike."""
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
    sentiment: str | None = None,
    description: str | None = None,
) -> dict:
    """Update an opinion. Only the provided fields are changed. sentiment must be one of:
    strongly_like, like, indifferent, dislike, strongly_dislike."""
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)
