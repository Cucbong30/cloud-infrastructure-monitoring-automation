"""cloud provider and Entra identity

Revision ID: e6f8a1c93b20
Revises: d5e7b1c42a90
Create Date: 2026-11-05 19:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e6f8a1c93b20"
down_revision = "d5e7b1c42a90"
branch_labels = None
depends_on = None


def _column_names(table):
    return {row[1] for row in op.get_bind().exec_driver_sql(f"PRAGMA table_info({table})")}


def _index_names():
    return {row[0] for row in op.get_bind().exec_driver_sql("SELECT name FROM sqlite_master WHERE type='index'")}


def upgrade():
    # ADD COLUMN only. Rebuilding servers with batch mode drops the table and breaks
    # the foreign keys from alerts, jobs, and incidents.
    user_columns = _column_names("users")
    if "email" not in user_columns:
        op.add_column("users", sa.Column("email", sa.String(length=255), nullable=True))
    if "entra_oid" not in user_columns:
        op.add_column("users", sa.Column("entra_oid", sa.String(length=64), nullable=True))
    if "ix_users_entra_oid" not in _index_names():
        op.create_index("ix_users_entra_oid", "users", ["entra_oid"], unique=True)
    if "provider" not in _column_names("servers"):
        op.add_column(
            "servers",
            sa.Column("provider", sa.String(length=20), nullable=False, server_default="vmware"),
        )
    op.execute(sa.text("DROP TABLE IF EXISTS _alembic_tmp_servers"))


def downgrade():
    op.drop_index("ix_users_entra_oid", table_name="users")
    op.drop_column("servers", "provider")
    op.drop_column("users", "entra_oid")
    op.drop_column("users", "email")
