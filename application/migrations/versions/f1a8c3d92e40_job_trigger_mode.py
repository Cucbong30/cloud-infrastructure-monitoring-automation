"""manual trigger identity on automation jobs

Revision ID: f1a8c3d92e40
Revises: e6f8a1c93b20
Create Date: 2026-11-11 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "f1a8c3d92e40"
down_revision = "e6f8a1c93b20"
branch_labels = None
depends_on = None


def _column_names(table):
    return {row[1] for row in op.get_bind().exec_driver_sql(f"PRAGMA table_info({table})")}


def upgrade():
    # ADD COLUMN only. Rebuilding automation_jobs would drop the incident foreign key.
    columns = _column_names("automation_jobs")
    if "mode" not in columns:
        op.add_column("automation_jobs", sa.Column("mode", sa.String(length=10), nullable=True))
    if "triggered_by" not in columns:
        op.add_column("automation_jobs", sa.Column("triggered_by", sa.String(length=255), nullable=True))
    if "user_email" not in columns:
        op.add_column("automation_jobs", sa.Column("user_email", sa.String(length=255), nullable=True))
    if "user_role" not in columns:
        op.add_column("automation_jobs", sa.Column("user_role", sa.String(length=20), nullable=True))
    op.execute(
        """
        UPDATE automation_jobs
        SET mode = CASE
            WHEN trigger_source = 'manual' THEN 'MANUAL'
            WHEN trigger_source = 'remediation' AND requested_by IS NOT NULL THEN 'MANUAL'
            ELSE 'AUTO'
        END
        WHERE mode IS NULL
        """
    )


def downgrade():
    columns = _column_names("automation_jobs")
    if "user_role" in columns:
        op.drop_column("automation_jobs", "user_role")
    if "user_email" in columns:
        op.drop_column("automation_jobs", "user_email")
    if "triggered_by" in columns:
        op.drop_column("automation_jobs", "triggered_by")
    if "mode" in columns:
        op.drop_column("automation_jobs", "mode")
