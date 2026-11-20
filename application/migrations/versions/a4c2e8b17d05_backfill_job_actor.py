"""backfill manual and auto actor on existing jobs

Revision ID: a4c2e8b17d05
Revises: f1a8c3d92e40
Create Date: 2026-11-11 22:20:00.000000

"""
from alembic import op


revision = "a4c2e8b17d05"
down_revision = "f1a8c3d92e40"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE automation_jobs
        SET triggered_by = 'SYSTEM',
            user_role = 'SYSTEM'
        WHERE mode = 'AUTO'
          AND (triggered_by IS NULL OR triggered_by = '')
        """
    )
    op.execute(
        """
        UPDATE automation_jobs
        SET triggered_by = (
                SELECT CASE
                    WHEN users.email IS NOT NULL AND users.email != '' THEN users.email
                    ELSE users.username
                END
                FROM users
                WHERE users.id = automation_jobs.requested_by
            ),
            user_email = (
                SELECT NULLIF(users.email, '')
                FROM users
                WHERE users.id = automation_jobs.requested_by
            ),
            user_role = (
                SELECT users.role
                FROM users
                WHERE users.id = automation_jobs.requested_by
            )
        WHERE mode = 'MANUAL'
          AND requested_by IS NOT NULL
          AND (triggered_by IS NULL OR triggered_by = '')
        """
    )


def downgrade():
    pass
