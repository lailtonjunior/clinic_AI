"""add mfa secret

Revision ID: 0008_mfa_fields
Revises: 0007_rename_auditlog_metadata
Create Date: 2025-12-05
"""
from alembic import op
import sqlalchemy as sa


revision = "0008_mfa_fields"
down_revision = "0007_rename_auditlog_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("mfa_secret", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "mfa_secret")

