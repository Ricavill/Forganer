"""add user auth fields

Revision ID: 496bd194f238
Revises: 9b740d4dcec1
Create Date: 2026-08-19

"""
from alembic import op
import sqlalchemy as sa

revision = "496bd194f238"
down_revision = "9b740d4dcec1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("hashed_password", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "hashed_password")
