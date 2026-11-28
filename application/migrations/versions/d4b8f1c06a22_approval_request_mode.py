"""store the mode on an approval request

Revision ID: d4b8f1c06a22
Revises: c3a9e7b21f04
Create Date: 2026-11-20 18:00:00.000000

"""
import sqlalchemy as sa
from alembic import op


revision = "d4b8f1c06a22"
down_revision = "c3a9e7b21f04"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("approval_requests") as batch:
        batch.add_column(sa.Column("mode", sa.String(length=20), nullable=False, server_default="MANUAL"))


def downgrade():
    with op.batch_alter_table("approval_requests") as batch:
        batch.drop_column("mode")
