from contextlib import ExitStack
from unittest.mock import AsyncMock, patch

from app.core import llm, mcp_client
from app.features.bot_agent import service
from app.features.users.service import get_user_by_email


def _stub_dependencies(stack: ExitStack) -> None:
    stack.enter_context(patch.object(llm, "embed_text", AsyncMock(return_value=[0.0] * 1536)))
    stack.enter_context(patch.object(llm, "extract_memory", AsyncMock(return_value=None)))
    stack.enter_context(patch.object(service, "_search_memories", return_value=[]))
    stack.enter_context(patch.object(mcp_client, "list_openai_tools", AsyncMock(return_value=[])))


def test_tool_call_results_persist_across_turns(client, auth_headers, db_session):
    """A tool result from one chat turn (e.g. a looked-up user id) must still be
    visible to the model on a later turn in the same session - otherwise the
    model has to re-derive facts like ids from its own prose, which is unreliable."""
    headers = auth_headers("botagent1@test.com")
    get_user_by_email(db_session, "botagent1@test.com")

    with ExitStack() as stack:
        _stub_dependencies(stack)
        first_call = stack.enter_context(
            patch.object(
                llm,
                "generate_reply_with_tools",
                AsyncMock(return_value=("I found them, their id is 42.", ["find_user(x) -> {'id': 42}"])),
            )
        )
        response = client.post("/bot-agent/chat", json={"message": "find that user"}, headers=headers)
        assert response.status_code == 200

    with ExitStack() as stack:
        _stub_dependencies(stack)
        second_call = stack.enter_context(
            patch.object(llm, "generate_reply_with_tools", AsyncMock(return_value=("Done.", [])))
        )
        response = client.post(
            "/bot-agent/chat", json={"message": "now send them a request"}, headers=headers
        )
        assert response.status_code == 200

    second_call_messages = second_call.call_args.args[1]
    joined = " ".join(m["content"] for m in second_call_messages)
    assert "find_user(x) -> {'id': 42}" in joined
    assert first_call.await_count == 1
