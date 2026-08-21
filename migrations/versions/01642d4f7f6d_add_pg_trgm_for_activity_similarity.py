"""add pg_trgm for activity name similarity matching

Revision ID: 01642d4f7f6d
Revises: 45e7199d823d
Create Date: 2026-08-22

"""
from alembic import op

revision = "01642d4f7f6d"
down_revision = "45e7199d823d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE INDEX ix_activities_name_trgm ON activities USING gin (name gin_trgm_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_activities_name_trgm")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
