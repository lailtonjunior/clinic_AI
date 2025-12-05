from alembic import op
import sqlalchemy as sa

revision = "0003_rename_metadata_field"
down_revision = "0002_sigtap_fields"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "tabelas_auxiliares",
        "metadata",
        new_column_name="meta_json",
        existing_type=sa.JSON(),
        existing_nullable=True,
    )


def downgrade():
    op.alter_column(
        "tabelas_auxiliares",
        "meta_json",
        new_column_name="metadata",
        existing_type=sa.JSON(),
        existing_nullable=True,
    )
