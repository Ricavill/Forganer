"""initial schema

Revision ID: 9b740d4dcec1
Revises:
Create Date: 2026-08-19

"""
from alembic import op
import sqlalchemy as sa

revision = "9b740d4dcec1"
down_revision = None
branch_labels = None
depends_on = None

sentiment_enum = sa.Enum(
    "strongly_like",
    "like",
    "indifferent",
    "dislike",
    "strongly_dislike",
    name="sentiment",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
    )

    op.create_table(
        "schedules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
    )

    sentiment_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "user_opinions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("activity_id", sa.Integer(), sa.ForeignKey("activities.id"), nullable=False),
        sa.Column("sentiment", sentiment_enum, nullable=False),
    )

    op.create_table(
        "user_friends",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )

    op.create_table(
        "user_friends_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("user_friends_id", sa.Integer(), sa.ForeignKey("user_friends.id"), nullable=False),
    )

    op.create_table(
        "meet_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
    )

    op.create_table(
        "meet_group_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("meet_group_id", sa.Integer(), sa.ForeignKey("meet_groups.id"), nullable=False),
    )

    op.create_table(
        "meets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("schedule_id", sa.Integer(), sa.ForeignKey("schedules.id"), nullable=False),
        sa.Column("meet_group_id", sa.Integer(), sa.ForeignKey("meet_groups.id"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("meets")
    op.drop_table("meet_group_users")
    op.drop_table("meet_groups")
    op.drop_table("user_friends_members")
    op.drop_table("user_friends")
    op.drop_table("user_opinions")
    sentiment_enum.drop(op.get_bind(), checkfirst=True)
    op.drop_table("schedules")
    op.drop_table("activities")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
