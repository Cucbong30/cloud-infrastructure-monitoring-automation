"""five incident statuses and a timeline

Revision ID: e7c1a9d44b10
Revises: d4b8f1c06a22
Create Date: 2026-11-27 20:20:00.000000

Existing incident and job rows stay in place. open and resolved keep those
values. resolved_at is copied from the old closed_at so the resolve time is
not lost when closed_at later means a human close.
"""
import sqlalchemy as sa
from alembic import op


revision = "e7c1a9d44b10"
down_revision = "d4b8f1c06a22"
branch_labels = None
depends_on = None


def upgrade():
    # Jobs and approvals reference incidents. SQLite cannot drop the table while
    # those foreign keys are enforced, so the rebuild runs with checks off.
    op.execute("DROP TABLE IF EXISTS _alembic_tmp_incidents")
    with op.get_context().autocommit_block():
        op.execute("PRAGMA foreign_keys=OFF")
    with op.batch_alter_table("incidents") as batch:
        batch.add_column(sa.Column("severity", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("remediation_type", sa.String(length=20), nullable=True))
        batch.add_column(sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("acknowledged_by", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("progress_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("progress_by", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("closed_by", sa.Integer(), nullable=True))
        batch.drop_constraint("ck_incidents_status", type_="check")
        batch.create_check_constraint(
            "ck_incidents_status",
            "status IN ('open', 'acknowledged', 'in_progress', 'resolved', 'closed')",
        )
    with op.get_context().autocommit_block():
        op.execute("PRAGMA foreign_keys=ON")
    op.execute(
        "UPDATE incidents SET resolved_at = closed_at "
        "WHERE status = 'resolved' AND resolved_at IS NULL"
    )
    op.create_table(
        "incident_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=True),
        sa.Column("to_status", sa.String(length=20), nullable=False),
        sa.Column("event_key", sa.String(length=40), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=False, server_default=""),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("actor_name", sa.String(length=255), nullable=False, server_default="SYSTEM"),
        sa.Column("actor_role", sa.String(length=20), nullable=False, server_default="SYSTEM"),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("approval_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_incident_events_incident_id", "incident_events", ["incident_id"])
    op.execute(
        "INSERT INTO incident_events "
        "(incident_id, from_status, to_status, event_key, message, actor_name, actor_role, created_at) "
        "SELECT id, NULL, 'open', 'detected', 'Incident detected', 'SYSTEM', 'SYSTEM', opened_at "
        "FROM incidents"
    )
    op.execute(
        "INSERT INTO incident_events "
        "(incident_id, from_status, to_status, event_key, message, actor_name, actor_role, created_at) "
        "SELECT id, 'open', 'resolved', 'resolved', 'Incident resolved', 'SYSTEM', 'SYSTEM', "
        "COALESCE(resolved_at, closed_at, opened_at) FROM incidents WHERE status = 'resolved'"
    )


def downgrade():
    op.drop_index("ix_incident_events_incident_id", table_name="incident_events")
    op.drop_table("incident_events")
    with op.batch_alter_table("incidents") as batch:
        batch.drop_constraint("ck_incidents_status", type_="check")
        batch.create_check_constraint("ck_incidents_status", "status IN ('open', 'resolved')")
        batch.drop_column("closed_by")
        batch.drop_column("resolved_at")
        batch.drop_column("progress_by")
        batch.drop_column("progress_at")
        batch.drop_column("acknowledged_by")
        batch.drop_column("acknowledged_at")
        batch.drop_column("remediation_type")
        batch.drop_column("severity")
