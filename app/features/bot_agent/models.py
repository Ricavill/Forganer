import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.core.db import AuditMixin, Base


class MessageDirection(enum.IntEnum):
    IN = 1
    OUT = 2


class BotAgentSession(Base, AuditMixin):
    __tablename__ = "bot_agent_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str | None] = mapped_column(String(255))
    summary: Mapped[str | None] = mapped_column(Text)

    messages: Mapped[list["BotAgentMessage"]] = relationship(back_populates="session")


class BotAgentMessage(Base, AuditMixin):
    __tablename__ = "bot_agent_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    bot_agent_session_id: Mapped[int] = mapped_column(ForeignKey("bot_agent_sessions.id"))
    text: Mapped[str] = mapped_column(Text)
    direction: Mapped[int] = mapped_column(SmallInteger)

    session: Mapped[BotAgentSession] = relationship(back_populates="messages")


class BotAgentMemory(Base, AuditMixin):
    """Semantic memory: standalone facts about a user, searchable by embedding similarity."""

    __tablename__ = "bot_agent_memories"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    bot_agent_session_id: Mapped[int | None] = mapped_column(ForeignKey("bot_agent_sessions.id"))
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(settings.openai_embedding_dimensions))
