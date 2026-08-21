"""add audit fields

Revision ID: 0d8e76216799
Revises: 496bd194f238
Create Date: 2026-08-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0d8e76216799"
down_revision = "496bd194f238"
branch_labels = None
depends_on = None

TABLES = [
    "users",
    "activities",
    "schedules",
    "user_opinions",
    "user_friends",
    "user_friends_members",
    "meet_groups",
    "meet_group_users",
    "meets",
]


def upgrade() -> None:
    for table in TABLES:
        op.add_column(
            table,
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.add_column(
            table,
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        )
        op.add_column(table, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    for table in TABLES:
        op.drop_column(table, "deleted_at")
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")
