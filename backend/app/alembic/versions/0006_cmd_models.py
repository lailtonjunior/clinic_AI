"""cmd models

Revision ID: 0006_cmd_models
Revises: 0005_user_flags
Create Date: 2025-11-25
"""
from alembic import op
import sqlalchemy as sa


revision = "0006_cmd_models"
down_revision = "0005_user_flags"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cmd_config_tenant",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False, unique=True),
        sa.Column("cnes_estabelecimento", sa.String(length=7), nullable=False),
        sa.Column("wsdl_url", sa.String(length=255), nullable=False),
        sa.Column("usuario_servico", sa.String(length=100), nullable=False),
        sa.Column("senha_servico", sa.String(length=200), nullable=False),
        sa.Column("cpf_operador", sa.String(length=11), nullable=False),
        sa.Column("senha_operador", sa.String(length=200), nullable=False),
        sa.Column("ambiente", sa.String(length=20), nullable=False, server_default="HOMOLOG"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    op.create_table(
        "cmd_contatos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False, index=True),
        sa.Column("paciente_id", sa.Integer(), sa.ForeignKey("pacientes.id"), nullable=False),
        sa.Column("unidade_id", sa.Integer(), sa.ForeignKey("unidades.id"), nullable=False),
        sa.Column("atendimento_id", sa.Integer(), sa.ForeignKey("atendimentos.id"), nullable=True),
        sa.Column("codigo_cmd_uuid", sa.String(length=36), nullable=True),
        sa.Column("competencia", sa.String(length=6), nullable=False),
        sa.Column("data_admissao", sa.Date(), nullable=False),
        sa.Column("data_desfecho", sa.Date(), nullable=True),
        sa.Column("modalidade_assistencial", sa.String(length=10), nullable=True),
        sa.Column("tipo_atendimento", sa.String(length=10), nullable=True),
        sa.Column("cid_principal", sa.String(length=10), nullable=True),
        sa.Column("cids_associados", sa.JSON(), nullable=True),
        sa.Column("resumo_procedimentos", sa.JSON(), nullable=True),
        sa.Column("status_envio_cmd", sa.String(length=20), nullable=False, server_default="PENDENTE"),
        sa.Column("ultimo_erro_cmd", sa.Text(), nullable=True),
        sa.Column("data_ultimo_envio_cmd", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_cmdcontato_tenant_competencia", "cmd_contatos", ["tenant_id", "competencia"])
    op.create_index("idx_cmdcontato_uuid", "cmd_contatos", ["codigo_cmd_uuid"])


def downgrade() -> None:
    op.drop_index("idx_cmdcontato_uuid", table_name="cmd_contatos")
    op.drop_index("idx_cmdcontato_tenant_competencia", table_name="cmd_contatos")
    op.drop_table("cmd_contatos")
    op.drop_table("cmd_config_tenant")
