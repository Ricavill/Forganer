"""make schedule dates timezone-aware

Revision ID: 45e7199d823d
Revises: d994b17ffd1d
Create Date: 2026-08-21

"""
from alembic import op
import sqlalchemy as sa

revision = "45e7199d823d"
down_revision = "d994b17ffd1d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "schedules",
        "start_date",
        type_=sa.DateTime(timezone=True),
        postgresql_using="start_date AT TIME ZONE 'UTC'",
    )
    op.alter_column(
        "schedules",
        "end_date",
        type_=sa.DateTime(timezone=True),
        postgresql_using="end_date AT TIME ZONE 'UTC'",
    )


def downgrade() -> None:
    op.alter_column("schedules", "start_date", type_=sa.DateTime(timezone=False))
    op.alter_column("schedules", "end_date", type_=sa.DateTime(timezone=False))
