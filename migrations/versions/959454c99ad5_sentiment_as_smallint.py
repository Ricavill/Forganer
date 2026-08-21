"""store sentiment as smallint instead of a native enum

Revision ID: 959454c99ad5
Revises: 01642d4f7f6d
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "959454c99ad5"
down_revision = "01642d4f7f6d"
branch_labels = None
depends_on = None

LABEL_TO_INT = {
    "strongly_dislike": 1,
    "dislike": 2,
    "indifferent": 3,
    "like": 4,
    "strongly_like": 5,
}

sentiment_enum = sa.Enum(
    "strongly_like",
    "like",
    "indifferent",
    "dislike",
    "strongly_dislike",
    name="sentiment",
)


def _case_sql(mapping: dict) -> str:
    cases = " ".join(f"WHEN '{k}' THEN {v}" for k, v in mapping.items())
    return f"CASE sentiment::text {cases} END"


def upgrade() -> None:
    op.execute(f"ALTER TABLE user_opinions ALTER COLUMN sentiment TYPE smallint USING ({_case_sql(LABEL_TO_INT)})")
    sentiment_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    sentiment_enum.create(op.get_bind(), checkfirst=True)
    cases = " ".join(f"WHEN {v} THEN '{k}'" for k, v in LABEL_TO_INT.items())
    op.execute(
        f"ALTER TABLE user_opinions ALTER COLUMN sentiment TYPE sentiment "
        f"USING ((CASE sentiment {cases} END)::sentiment)"
    )
