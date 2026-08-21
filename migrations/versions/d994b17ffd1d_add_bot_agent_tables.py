"""add bot agent tables

Revision ID: d994b17ffd1d
Revises: 0d8e76216799
Create Date: 2026-08-21

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "d994b17ffd1d"
down_revision = "0d8e76216799"
branch_labels = None
depends_on = None

message_direction_enum = postgresql.ENUM("in", "out", name="message_direction", create_type=False)

AUDIT_COLUMNS = [
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
]


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "bot_agent_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        *[c.copy() for c in AUDIT_COLUMNS],
    )

    message_direction_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "bot_agent_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("bot_agent_session_id", sa.Integer(), sa.ForeignKey("bot_agent_sessions.id"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("direction", message_direction_enum, nullable=False),
        *[c.copy() for c in AUDIT_COLUMNS],
    )

    op.create_table(
        "bot_agent_memories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("bot_agent_session_id", sa.Integer(), sa.ForeignKey("bot_agent_sessions.id"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        *[c.copy() for c in AUDIT_COLUMNS],
    )


def downgrade() -> None:
    op.drop_table("bot_agent_memories")
    op.drop_table("bot_agent_messages")
    message_direction_enum.drop(op.get_bind(), checkfirst=True)
    op.drop_table("bot_agent_sessions")
