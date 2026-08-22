"""store message direction as smallint instead of a native enum

Revision ID: 8311752bd469
Revises: 959454c99ad5
Create Date: 2026-08-22

"""
from alembic import op
import sqlalchemy as sa

revision = "8311752bd469"
down_revision = "959454c99ad5"
branch_labels = None
depends_on = None

LABEL_TO_INT = {"in": 1, "out": 2}

direction_enum = sa.Enum("in", "out", name="message_direction")


def _case_sql(mapping: dict, column: str) -> str:
    cases = " ".join(f"WHEN '{k}' THEN {v}" for k, v in mapping.items())
    return f"CASE {column}::text {cases} END"


def upgrade() -> None:
    op.execute(
        f"ALTER TABLE bot_agent_messages ALTER COLUMN direction TYPE smallint "
        f"USING ({_case_sql(LABEL_TO_INT, 'direction')})"
    )
    direction_enum.drop(op.get_bind(), checkfirst=True)


def downgrade() -> None:
    direction_enum.create(op.get_bind(), checkfirst=True)
    cases = " ".join(f"WHEN {v} THEN '{k}'" for k, v in LABEL_TO_INT.items())
    op.execute(
        "ALTER TABLE bot_agent_messages ALTER COLUMN direction TYPE message_direction "
        f"USING ((CASE direction {cases} END)::message_direction)"
    )
