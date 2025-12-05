"""rename auditlog metadata column

Revision ID: 0007_rename_auditlog_metadata
Revises: 0006_cmd_models
Create Date: 2025-11-26
"""
from alembic import op
import sqlalchemy as sa


revision = "0007_rename_auditlog_metadata"
down_revision = "0006_cmd_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.alter_column("metadata", new_column_name="meta_json", existing_type=sa.JSON(), existing_nullable=True)


def downgrade() -> None:
    with op.batch_alter_table("audit_logs") as batch_op:
        batch_op.alter_column("meta_json", new_column_name="metadata", existing_type=sa.JSON(), existing_nullable=True)
