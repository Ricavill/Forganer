import httpx
from config import settings


class ApiClient:
    """Forwards calls to the Friends Activity Planner API using whichever bearer
    token the MCP caller supplies, so the API sees the request as coming from
    that same user."""

    def __init__(self) -> None:
        self._client = httpx.AsyncClient(base_url=settings.api_base_url)

    async def request(self, method: str, path: str, token: str, **kwargs) -> httpx.Response:
        headers = {"Authorization": token if token.lower().startswith("bearer ") else f"Bearer {token}"}
        return await self._client.request(method, path, headers=headers, **kwargs)

    async def aclose(self) -> None:
        await self._client.aclose()


api_client = ApiClient()
