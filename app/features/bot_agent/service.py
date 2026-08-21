from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import llm
from app.core.config import settings
from app.features.bot_agent.models import BotAgentMemory, BotAgentMessage, BotAgentSession, MessageDirection
from app.features.bot_agent.schemas import ChatResponse
from app.features.users.models import User


def _is_today(dt: datetime) -> bool:
    return dt.astimezone(timezone.utc).date() == datetime.now(timezone.utc).date()


async def _get_session_messages(db: AsyncSession, session_id: int) -> list[BotAgentMessage]:
    result = await db.execute(
        select(BotAgentMessage)
        .where(BotAgentMessage.bot_agent_session_id == session_id)
        .order_by(BotAgentMessage.created_at)
    )
    return list(result.scalars().all())


def _format_transcript(messages: list[BotAgentMessage]) -> str:
    lines = [f"{'User' if m.direction == MessageDirection.IN else 'Assistant'}: {m.text}" for m in messages]
    return "\n".join(lines)


async def _get_active_session(db: AsyncSession, user: User) -> BotAgentSession:
    result = await db.execute(
        select(BotAgentSession)
        .where(BotAgentSession.user_id == user.id)
        .order_by(BotAgentSession.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    if latest is not None and _is_today(latest.created_at):
        return latest

    new_summary = None
    if latest is not None:
        old_messages = await _get_session_messages(db, latest.id)
        if old_messages:
            new_summary = await llm.summarize_conversation(_format_transcript(old_messages), latest.summary)
        else:
            new_summary = latest.summary

    session = BotAgentSession(user_id=user.id, title="Chat", summary=new_summary)
    db.add(session)
    await db.flush()
    return session


async def _add_message(db: AsyncSession, session_id: int, text: str, direction: MessageDirection) -> BotAgentMessage:
    message = BotAgentMessage(bot_agent_session_id=session_id, text=text, direction=direction)
    db.add(message)
    await db.flush()
    return message


async def _search_memories(db: AsyncSession, user_id: int, embedding: list[float]) -> list[BotAgentMemory]:
    result = await db.execute(
        select(BotAgentMemory)
        .where(BotAgentMemory.user_id == user_id)
        .order_by(BotAgentMemory.embedding.cosine_distance(embedding))
        .limit(settings.bot_agent_memory_top_k)
    )
    return list(result.scalars().all())


async def _store_memory(db: AsyncSession, user_id: int, session_id: int, content: str) -> None:
    embedding = await llm.embed_text(content)
    db.add(BotAgentMemory(user_id=user_id, bot_agent_session_id=session_id, content=content, embedding=embedding))


def _build_system_prompt(summary: str | None, memories: list[BotAgentMemory]) -> str:
    parts = [llm.SYSTEM_PROMPT]
    if summary:
        parts.append(f"Summary of earlier conversations with this user:\n{summary}")
    if memories:
        facts = "\n".join(f"- {m.content}" for m in memories)
        parts.append(f"Known facts about this user from past sessions:\n{facts}")
    return "\n\n".join(parts)


async def chat(db: AsyncSession, user: User, message: str) -> ChatResponse:
    session = await _get_active_session(db, user)

    await _add_message(db, session.id, message, MessageDirection.IN)

    history = await _get_session_messages(db, session.id)
    history = history[-settings.bot_agent_history_limit :]
    chat_messages = [
        {"role": "user" if m.direction == MessageDirection.IN else "assistant", "content": m.text} for m in history
    ]

    query_embedding = await llm.embed_text(message)
    memories = await _search_memories(db, user.id, query_embedding)

    system_prompt = _build_system_prompt(session.summary, memories)
    reply = await llm.generate_reply(system_prompt, chat_messages)

    await _add_message(db, session.id, reply, MessageDirection.OUT)

    memory_fact = await llm.extract_memory(message, reply)
    if memory_fact:
        await _store_memory(db, user.id, session.id, memory_fact)

    await db.commit()
    return ChatResponse(session_id=session.id, reply=reply)
