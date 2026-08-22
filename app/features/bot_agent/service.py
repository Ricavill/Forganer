from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core import llm, mcp_client
from app.core.config import settings
from app.core.security import create_access_token
from app.features.bot_agent.models import BotAgentMemory, BotAgentMessage, BotAgentSession, MessageDirection
from app.features.bot_agent.schemas import ChatResponse


def _is_today(dt: datetime) -> bool:
    return dt.astimezone(timezone.utc).date() == datetime.now(timezone.utc).date()


def _get_session_messages(db: Session, session_id: int) -> list[BotAgentMessage]:
    result = db.execute(
        select(BotAgentMessage)
        .where(BotAgentMessage.bot_agent_session_id == session_id)
        .order_by(BotAgentMessage.created_at)
    )
    return list(result.scalars().all())


def _format_transcript(messages: list[BotAgentMessage]) -> str:
    lines = [
        f"{'User' if m.direction == MessageDirection.IN else 'Assistant'}: {m.text}"
        for m in messages
        if m.direction != MessageDirection.TOOL_LOG
    ]
    return "\n".join(lines)


def _message_to_chat_dict(m: BotAgentMessage) -> dict:
    if m.direction == MessageDirection.IN:
        return {"role": "user", "content": m.text}
    if m.direction == MessageDirection.TOOL_LOG:
        return {"role": "assistant", "content": f"[Tool result noted earlier in this conversation] {m.text}"}
    return {"role": "assistant", "content": m.text}


def _get_latest_session(db: Session, user_id: int) -> BotAgentSession | None:
    result = db.execute(
        select(BotAgentSession)
        .where(BotAgentSession.user_id == user_id)
        .order_by(BotAgentSession.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


def _create_session(db: Session, user_id: int, summary: str | None) -> BotAgentSession:
    session = BotAgentSession(user_id=user_id, title="Chat", summary=summary)
    db.add(session)
    db.flush()
    return session


async def _get_active_session(db: Session, user_id: int) -> BotAgentSession:
    latest = await run_in_threadpool(_get_latest_session, db, user_id)

    if latest is not None and _is_today(latest.created_at):
        return latest

    new_summary = None
    if latest is not None:
        old_messages = await run_in_threadpool(_get_session_messages, db, latest.id)
        if old_messages:
            new_summary = await llm.summarize_conversation(_format_transcript(old_messages), latest.summary)
        else:
            new_summary = latest.summary

    return await run_in_threadpool(_create_session, db, user_id, new_summary)


def _add_message(db: Session, session_id: int, text: str, direction: MessageDirection) -> BotAgentMessage:
    message = BotAgentMessage(bot_agent_session_id=session_id, text=text, direction=direction)
    db.add(message)
    db.flush()
    return message


def _search_memories(db: Session, user_id: int, embedding: list[float]) -> list[BotAgentMemory]:
    result = db.execute(
        select(BotAgentMemory)
        .where(BotAgentMemory.user_id == user_id)
        .order_by(BotAgentMemory.embedding.cosine_distance(embedding))
        .limit(settings.bot_agent_memory_top_k)
    )
    return list(result.scalars().all())


def _add_memory(db: Session, user_id: int, session_id: int, content: str, embedding: list[float]) -> None:
    db.add(
        BotAgentMemory(user_id=user_id, bot_agent_session_id=session_id, content=content, embedding=embedding)
    )


def _build_system_prompt(summary: str | None, memories: list[BotAgentMemory]) -> str:
    parts = [llm.SYSTEM_PROMPT]
    if settings.resend_api_key:
        parts.append(llm.EMAIL_INVITE_PROMPT)
    if summary:
        parts.append(f"Summary of earlier conversations with this user:\n{summary}")
    if memories:
        facts = "\n".join(f"- {m.content}" for m in memories)
        parts.append(f"Known facts about this user from past sessions:\n{facts}")
    return "\n\n".join(parts)


async def chat(db: Session, user_id: int, user_email: str, message: str) -> ChatResponse:
    session = await _get_active_session(db, user_id)

    await run_in_threadpool(_add_message, db, session.id, message, MessageDirection.IN)

    history = await run_in_threadpool(_get_session_messages, db, session.id)
    history = history[-settings.bot_agent_history_limit :]
    chat_messages = [_message_to_chat_dict(m) for m in history]

    query_embedding = await llm.embed_text(message)
    memories = await run_in_threadpool(_search_memories, db, user_id, query_embedding)

    system_prompt = _build_system_prompt(session.summary, memories)

    agent_token = create_access_token(user_email)
    tools = await mcp_client.list_openai_tools(agent_token)

    async def call_tool(name: str, arguments: dict) -> str:
        return await mcp_client.call_tool(agent_token, name, arguments)

    reply, tool_log = await llm.generate_reply_with_tools(system_prompt, chat_messages, tools, call_tool)

    for entry in tool_log:
        await run_in_threadpool(_add_message, db, session.id, entry, MessageDirection.TOOL_LOG)

    await run_in_threadpool(_add_message, db, session.id, reply, MessageDirection.OUT)

    memory_fact = await llm.extract_memory(message, reply)
    if memory_fact:
        memory_embedding = await llm.embed_text(memory_fact)
        await run_in_threadpool(_add_memory, db, user_id, session.id, memory_fact, memory_embedding)

    await run_in_threadpool(db.commit)
    return ChatResponse(session_id=session.id, reply=reply)
