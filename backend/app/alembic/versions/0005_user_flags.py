"""user flags and timestamps

Revision ID: 0005_user_flags
Revises: 0004_rbac_tenant_roles
Create Date: 2025-11-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0005_user_flags"
down_revision = "0004_rbac_tenant_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("usuarios", sa.Column("updated_at", sa.DateTime(), nullable=True))
    op.add_column("usuarios", sa.Column("must_change_password", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("usuarios", "must_change_password")
    op.drop_column("usuarios", "updated_at")
