"""add icp brasil signature fields

Revision ID: 0009_icp_brasil_fields
Revises: 0008_mfa_fields
Create Date: 2025-12-07
"""
from alembic import op
import sqlalchemy as sa


revision = "0009_icp_brasil_fields"
down_revision = "0008_mfa_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("evolucoes_prontuario", sa.Column("assinatura_modo", sa.String(length=20), nullable=False, server_default="NONE"))
    op.add_column("evolucoes_prontuario", sa.Column("assinatura_hash", sa.String(length=128), nullable=True))
    op.add_column("evolucoes_prontuario", sa.Column("assinatura_metadata", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("evolucoes_prontuario", "assinatura_metadata")
    op.drop_column("evolucoes_prontuario", "assinatura_hash")
    op.drop_column("evolucoes_prontuario", "assinatura_modo")
