"""approval requests for medium and high actions

Revision ID: c3a9e7b21f04
Revises: a4c2e8b17d05
Create Date: 2026-11-18 20:10:00.000000

"""
import sqlalchemy as sa
from alembic import op


revision = "c3a9e7b21f04"
down_revision = "a4c2e8b17d05"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("server_id", sa.Integer(), nullable=True),
        sa.Column("alert_id", sa.Integer(), nullable=True),
        sa.Column("job_id", sa.Integer(), nullable=True),
        sa.Column("incident_id", sa.Integer(), nullable=True),
        sa.Column("requester_id", sa.Integer(), nullable=True),
        sa.Column("approver_id", sa.Integer(), nullable=True),
        sa.Column("action_key", sa.String(length=80), nullable=False),
        sa.Column("service", sa.String(length=40), nullable=False),
        sa.Column("risk", sa.String(length=10), nullable=False),
        sa.Column("parameters_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("requester_name", sa.String(length=255), nullable=False),
        sa.Column("requester_role", sa.String(length=20), nullable=False),
        sa.Column("approver_name", sa.String(length=255), nullable=True),
        sa.Column("approver_role", sa.String(length=20), nullable=True),
        sa.Column("decision", sa.String(length=30), nullable=True),
        sa.Column("decision_reason", sa.String(length=200), nullable=True),
        sa.Column("execution_result", sa.String(length=20), nullable=True),
        sa.Column("verification_result", sa.String(length=20), nullable=True),
        sa.Column("final_status", sa.String(length=40), nullable=True),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("decision_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("execution_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["server_id"], ["servers.id"], ondelete="SET NULL", name="fk_approval_requests_server_id"),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="SET NULL", name="fk_approval_requests_alert_id"),
        sa.ForeignKeyConstraint(["job_id"], ["automation_jobs.id"], ondelete="SET NULL", name="fk_approval_requests_job_id"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="SET NULL", name="fk_approval_requests_incident_id"),
        sa.ForeignKeyConstraint(["requester_id"], ["users.id"], ondelete="SET NULL", name="fk_approval_requests_requester_id"),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"], ondelete="SET NULL", name="fk_approval_requests_approver_id"),
        sa.CheckConstraint(
            "status IN ('PENDING_APPROVAL', 'APPROVED', 'REJECTED', 'APPROVAL_EXPIRED')",
            name="ck_approval_requests_status",
        ),
        sa.CheckConstraint("risk IN ('MEDIUM', 'HIGH')", name="ck_approval_requests_risk"),
    )
    op.create_index("ix_approval_requests_status", "approval_requests", ["status"])
    op.create_index("ix_approval_requests_server_id", "approval_requests", ["server_id"])


def downgrade():
    op.drop_index("ix_approval_requests_server_id", table_name="approval_requests")
    op.drop_index("ix_approval_requests_status", table_name="approval_requests")
    op.drop_table("approval_requests")
