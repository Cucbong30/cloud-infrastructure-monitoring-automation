"""allow auto as a job trigger

Revision ID: c8d4f0a21b36
Revises: b7e2a91c4d08
Create Date: 2026-11-02 21:00:00.000000

"""
from alembic import op


revision = "c8d4f0a21b36"
down_revision = "b7e2a91c4d08"
branch_labels = None
depends_on = None

TRIGGER = "trigger_source IN ('manual', 'remediation', 'system', 'auto')"
PREVIOUS = "trigger_source IN ('manual', 'remediation', 'system')"


def upgrade():
    with op.batch_alter_table("automation_jobs") as batch:
        batch.drop_constraint("ck_automation_jobs_trigger_source", type_="check")
        batch.create_check_constraint("ck_automation_jobs_trigger_source", TRIGGER)


def downgrade():
    with op.batch_alter_table("automation_jobs") as batch:
        batch.drop_constraint("ck_automation_jobs_trigger_source", type_="check")
        batch.create_check_constraint("ck_automation_jobs_trigger_source", PREVIOUS)
