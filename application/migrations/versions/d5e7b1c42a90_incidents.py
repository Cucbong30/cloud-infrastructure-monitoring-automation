"""incidents and per-job attempt

Revision ID: d5e7b1c42a90
Revises: c8d4f0a21b36
Create Date: 2026-11-04 20:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d5e7b1c42a90"
down_revision = "c8d4f0a21b36"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("server_id", sa.Integer(), sa.ForeignKey("servers.id"), nullable=False),
        sa.Column("alert_id", sa.Integer(), sa.ForeignKey("alerts.id"), nullable=True),
        sa.Column("action_key", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("manual_required", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("verification_failed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("blocked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("reason", sa.String(length=80), nullable=True),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('open', 'resolved')", name="ck_incidents_status"),
    )
    op.create_index("ix_incidents_server_action", "incidents", ["server_id", "action_key", "status"])
    with op.batch_alter_table("automation_jobs") as batch:
        batch.add_column(sa.Column("incident_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("attempt", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("final_status", sa.String(length=40), nullable=True))
        batch.add_column(sa.Column("reason", sa.String(length=80), nullable=True))
        batch.create_foreign_key("fk_automation_jobs_incident_id", "incidents", ["incident_id"], ["id"])


def downgrade():
    with op.batch_alter_table("automation_jobs") as batch:
        batch.drop_constraint("fk_automation_jobs_incident_id", type_="foreignkey")
        batch.drop_column("reason")
        batch.drop_column("final_status")
        batch.drop_column("attempt")
        batch.drop_column("incident_id")
    op.drop_index("ix_incidents_server_action", table_name="incidents")
    op.drop_table("incidents")
