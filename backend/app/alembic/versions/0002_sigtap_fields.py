from alembic import op
import sqlalchemy as sa

revision = "0002_sigtap_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tabelas_sigtap", sa.Column("exige_cid", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tabelas_sigtap", sa.Column("exige_apac", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("tabelas_sigtap", sa.Column("doc_paciente", sa.String(length=20), nullable=False, server_default="AMBOS_PERMITIDOS"))
    op.add_column("tabelas_sigtap", sa.Column("sexo_permitido", sa.String(length=1), nullable=False, server_default="A"))
    op.add_column("tabelas_sigtap", sa.Column("idade_min", sa.Integer(), nullable=True))
    op.add_column("tabelas_sigtap", sa.Column("idade_max", sa.Integer(), nullable=True))
    op.add_column("tabelas_sigtap", sa.Column("vigencia_inicio", sa.String(length=6), nullable=True))
    op.add_column("tabelas_sigtap", sa.Column("vigencia_fim", sa.String(length=6), nullable=True))


def downgrade():
    op.drop_column("tabelas_sigtap", "vigencia_fim")
    op.drop_column("tabelas_sigtap", "vigencia_inicio")
    op.drop_column("tabelas_sigtap", "idade_max")
    op.drop_column("tabelas_sigtap", "idade_min")
    op.drop_column("tabelas_sigtap", "sexo_permitido")
    op.drop_column("tabelas_sigtap", "doc_paciente")
    op.drop_column("tabelas_sigtap", "exige_apac")
    op.drop_column("tabelas_sigtap", "exige_cid")
