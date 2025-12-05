"""rbac and audit log

Revision ID: 0004_rbac_tenant_roles
Revises: 0003_rename_metadata_field
Create Date: 2025-11-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0004_rbac_tenant_roles"
down_revision = "0003_rename_metadata_field"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tenant_user_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "tenant_id", "role", name="uq_user_tenant_role"),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("usuarios.id"), nullable=False, index=True),
        sa.Column("acao", sa.String(length=100), nullable=False),
        sa.Column("entidade", sa.String(length=100), nullable=False),
        sa.Column("entidade_id", sa.String(length=50), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now(), index=True),
    )
    op.add_column("usuarios", sa.Column("created_at", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("usuarios", "created_at")
    op.drop_table("audit_logs")
    op.drop_table("tenant_user_roles")
