"""add friend invitations table

Revision ID: cd184af27d92
Revises: 8311752bd469
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "cd184af27d92"
down_revision = "8311752bd469"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "friend_invitations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("from_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_friend_invitations_to_user_id", "friend_invitations", ["to_user_id"])


def downgrade() -> None:
    op.drop_index("ix_friend_invitations_to_user_id", table_name="friend_invitations")
    op.drop_table("friend_invitations")
