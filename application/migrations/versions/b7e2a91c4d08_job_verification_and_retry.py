"""job verification, stderr, and retry link

Revision ID: b7e2a91c4d08
Revises: 7dc527d28c3d
Create Date: 2026-10-28 19:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7e2a91c4d08"
down_revision = "7dc527d28c3d"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("automation_jobs") as batch:
        batch.add_column(sa.Column("stderr_excerpt", sa.Text(), nullable=True))
        batch.add_column(sa.Column("verification_result", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("verification_detail", sa.Text(), nullable=True))
        batch.add_column(sa.Column("block_reason", sa.Text(), nullable=True))
        batch.add_column(sa.Column("retry_of_job_id", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("automation_jobs") as batch:
        batch.drop_column("retry_of_job_id")
        batch.drop_column("block_reason")
        batch.drop_column("verification_detail")
        batch.drop_column("verification_result")
        batch.drop_column("stderr_excerpt")
