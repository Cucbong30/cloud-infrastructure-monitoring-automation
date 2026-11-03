from sqlalchemy import func, select

from app.extensions import db
from app.models import AuditLog
from app.services.checklog import observe_hosts


def _host(status):
    return {
        "name": "WEB01",
        "exporter": "UP",
        "exporter_label": "Node Exporter :9100",
        "services": [{"name": "Nginx :80", "status": "UP"}],
        "management": {"label": "SSH", "port": 22, "status": status, "text": f"SSH {status}"},
    }


def test_management_event_includes_remediation_detail():
    from types import SimpleNamespace

    from app.blueprints.dashboard import _check_event

    row = SimpleNamespace(
        action="check.down",
        details_json=(
            '{"check": "SSH :22", "host": "APP01", "kind": "management", '
            '"message": "APP01 SSH :22 is down", "status": "DOWN"}'
        ),
        created_at=None,
    )
    event = _check_event(row)
    assert event["title"] == "APP01 SSH :22 is down"
    assert "Remediation unavailable" in event["message"]
    assert "restart_container" in event["message"]
    assert "playbook was not started" in event["message"]
    up = SimpleNamespace(
        action="check.up",
        details_json=(
            '{"check": "SSH :22", "host": "APP01", "kind": "management", '
            '"message": "APP01 SSH :22 is up", "status": "UP"}'
        ),
        created_at=None,
    )
    restored = _check_event(up)
    assert "Remediation available" in restored["message"]
    assert "can run" in restored["message"]


def test_check_log_records_each_change_once(app):
    with app.app_context():
        observe_hosts([_host("UP")])
        observe_hosts([_host("UP")])
        assert db.session.scalar(select(func.count()).select_from(AuditLog).where(AuditLog.action == "check.up")) == 3
        observe_hosts([_host("DOWN")])
        down = db.session.scalar(
            select(AuditLog).where(AuditLog.resource_id == "WEB01:management", AuditLog.action == "check.down")
        )
        assert down is not None
        assert "WEB01 SSH :22 is down" in down.details_json
        observe_hosts([_host("UP")])
        observe_hosts([_host("UP")])
        rows = db.session.scalars(
            select(AuditLog).where(AuditLog.resource_id == "WEB01:management").order_by(AuditLog.id)
        ).all()
        assert [row.action for row in rows] == ["check.up", "check.down", "check.up"]
        assert "WEB01 SSH :22 is up" in rows[-1].details_json
