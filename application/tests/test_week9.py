"""Week 9: MEDIUM and HIGH actions wait for the right approver."""

from sqlalchemy import func, select

from app.executors.base import ExecutionResult
from app.extensions import db
from app.models import ApprovalRequest, AuditLog, AutomationJob, Server, User, utcnow
from tests.conftest import login, post_csrf


def _server(name):
    return db.session.scalar(select(Server).where(Server.name == name))


def _jobs():
    return db.session.scalar(select(func.count()).select_from(AutomationJob))


def _post_action(client, server_id, action, service):
    return post_csrf(
        client,
        "/automation/jobs",
        {
            "server_id": str(server_id),
            "action_key": action,
            "service": service,
            "mode": "MANUAL",
            "simulate": "success",
            "submit": "Trigger remediation",
        },
        page="/automation/",
    )


def _approval_id(response):
    location = response.headers["Location"]
    assert "/approvals/" in location
    return int(location.rstrip("/").rsplit("/", 1)[-1])


def test_low_action_still_runs_without_approval(seeded, client):
    login(client, "operator")
    cases = (
        ("WEB01", "restart_nginx", "Nginx"),
        ("APP01", "restart_container", "App"),
        ("WIN01", "restart_windows_exporter", "Windows Exporter"),
        ("AZURE01", "restart_nginx", "Nginx"),
    )
    with seeded.app_context():
        before = _jobs()
        pairs = [(_server(name).id, action, service) for name, action, service in cases]
    for server_id, action, service in pairs:
        response = _post_action(client, server_id, action, service)
        assert response.status_code == 302
        assert "/automation/jobs/" in response.headers["Location"]
    with seeded.app_context():
        assert _jobs() == before + len(cases)
        assert db.session.scalar(select(func.count()).select_from(ApprovalRequest)) == 0


def test_medium_approval_runs_only_after_it_is_approved(seeded, client, monkeypatch):
    calls = {"count": 0}

    def execute(self, job, server, action):
        calls["count"] += 1
        return ExecutionResult(True, 0, "container restarted", utcnow(), utcnow())

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", execute)
    sent = []
    seeded.config["NOTIFY_TRANSPORT"] = lambda event, fields, recipients: sent.append((event, fields, recipients))
    seeded.config["ALERT_RECIPIENT_WARNING"] = "KLTN-Alert-Warning@cucbong.id.vn"
    seeded.config["ALERT_RECIPIENT_INFO"] = "KLTN-Alert-Info@cucbong.id.vn"
    login(client, "operator")
    with seeded.app_context():
        db.session.scalar(select(User).where(User.username == "admin")).email = "admin@cucbong.id.vn"
        db.session.scalar(select(User).where(User.username == "operator")).email = "operator@cucbong.id.vn"
        db.session.commit()
        server_id = _server("APP01").id
        before = _jobs()
    requested = _post_action(client, server_id, "restart_docker_service", "Docker")
    approval_id = _approval_id(requested)
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, approval_id)
        assert approval.status == "PENDING_APPROVAL"
        assert approval.risk == "MEDIUM"
        assert approval.mode == "MANUAL"
        assert approval.requester_role == "operator"
        assert approval.job_id is None
        assert _jobs() == before
    page = client.get(f"/automation/approvals/{approval_id}")
    assert b"PENDING_APPROVAL" in page.data
    assert b"approve-button" not in page.data
    denied = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/approve",
        {},
        page=f"/automation/approvals/{approval_id}",
    )
    assert denied.status_code == 403
    assert calls["count"] == 0
    requested_mail = [item for item in sent if item[0] == "approval_requested"]
    assert requested_mail
    assert requested_mail[0][1]["risk"] == "MEDIUM"
    assert requested_mail[0][1]["request_url"].endswith(f"/automation/approvals/{approval_id}")
    assert requested_mail[0][2] == ["admin@cucbong.id.vn"]
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "admin")
    admin_page = client.get(f"/automation/approvals/{approval_id}")
    assert b"approve-button" in admin_page.data
    approved = post_csrf(client, f"/automation/approvals/{approval_id}/approve", {}, page=f"/automation/approvals/{approval_id}")
    assert approved.status_code == 302
    assert calls["count"] == 1
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, approval_id)
        assert approval.status == "APPROVED"
        assert approval.decision == "APPROVED"
        assert approval.job_id is not None
        assert approval.incident_id is not None
        assert approval.final_status == "SUCCESS"
        assert approval.execution_result == "SUCCESS"
        job = db.session.get(AutomationJob, approval.job_id)
        assert job.action_key == "restart_docker_service"
    approved_mail = [item for item in sent if item[0] == "approval_approved"]
    assert approved_mail
    assert approved_mail[-1][2] == ["operator@cucbong.id.vn"]


def test_rejected_request_does_not_call_the_playbook(seeded, client, monkeypatch):
    calls = {"count": 0}
    monkeypatch.setattr(
        "app.executors.mock.MockExecutor.execute",
        lambda self, job, server, action: calls.__setitem__("count", calls["count"] + 1),
    )
    login(client, "operator")
    with seeded.app_context():
        server_id = _server("APP01").id
        before = _jobs()
    approval_id = _approval_id(_post_action(client, server_id, "restart_docker_service", "Docker"))
    blocked = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/reject",
        {"reason": "Operator cannot reject."},
        page=f"/automation/approvals/{approval_id}",
    )
    assert blocked.status_code == 403
    assert calls["count"] == 0
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "admin")
    rejected = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/reject",
        {"reason": "Change window is closed."},
        page=f"/automation/approvals/{approval_id}",
    )
    assert rejected.status_code == 302
    assert calls["count"] == 0
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, approval_id)
        assert approval.status == "REJECTED"
        assert approval.decision == "REJECTED"
        assert approval.job_id is None
        assert approval.execution_result == "NOT_RUN"
        assert _jobs() == before
        audit = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "approval.rejected",
                AuditLog.resource_id == str(approval_id),
            )
        )
        assert "Change window is closed." in audit.details_json
        assert '"requester_role": "operator"' in audit.details_json
        assert '"playbook_executed": false' in audit.details_json


def test_operator_cannot_request_or_approve_a_high_risk_action(seeded, client, monkeypatch):
    calls = {"count": 0}

    def execute(self, job, server, action):
        calls["count"] += 1
        return ExecutionResult(True, 0, "server rebooted", utcnow(), utcnow())

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", execute)
    login(client, "operator")
    with seeded.app_context():
        server_id = _server("AZURE01").id
        before = _jobs()
        approvals_before = db.session.scalar(select(func.count()).select_from(ApprovalRequest))
    denied = _post_action(client, server_id, "reboot_server", "Host")
    assert denied.status_code == 403
    assert b"Permission denied for Operator role" in denied.data
    assert calls["count"] == 0
    with seeded.app_context():
        assert _jobs() == before
        assert db.session.scalar(select(func.count()).select_from(ApprovalRequest)) == approvals_before
        audit = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "permission.denied").order_by(AuditLog.id.desc())
        )
        assert '"risk": "HIGH"' in audit.details_json
        assert "reboot_server" in audit.details_json
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "admin")
    approval_id = _approval_id(_post_action(client, server_id, "reboot_server", "Host"))
    with seeded.app_context():
        assert _jobs() == before
        assert db.session.get(ApprovalRequest, approval_id).job_id is None
    denied_again = post_csrf(client, "/logout", {}, page="/dashboard")
    assert denied_again.status_code == 302
    login(client, "operator")
    still_denied = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/approve",
        {},
        page="/automation/approvals",
    )
    assert still_denied.status_code == 403
    assert calls["count"] == 0
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "admin")
    approved = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/approve",
        {},
        page=f"/automation/approvals/{approval_id}",
    )
    assert approved.status_code == 302
    assert calls["count"] == 1
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, approval_id)
        assert approval.status == "APPROVED"
        assert approval.approver_role == "admin"
        assert approval.requester_role == "admin"
        detail = client.get(f"/automation/jobs/{approval.job_id}")
    assert b"HIGH" in detail.data
    assert b"APPROVED" in detail.data
    assert b"Job ID" in detail.data


def test_expired_approval_is_not_executed(seeded, client, monkeypatch):
    monkeypatch.setattr(
        "app.executors.mock.MockExecutor.execute",
        lambda self, job, server, action: (_ for _ in ()).throw(AssertionError("expired request must not run")),
    )
    seeded.config["APPROVAL_TIMEOUT_MINUTES"] = 0
    login(client, "operator")
    with seeded.app_context():
        server_id = _server("APP01").id
        before = _jobs()
    approval_id = _approval_id(_post_action(client, server_id, "restart_docker_service", "Docker"))
    page = client.get("/automation/approvals")
    assert b"APPROVAL_EXPIRED" in page.data
    denied = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/approve",
        {},
        page=f"/automation/approvals/{approval_id}",
    )
    assert denied.status_code == 403
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, approval_id)
        assert approval.status == "APPROVAL_EXPIRED"
        assert approval.job_id is None
        assert approval.execution_result == "NOT_RUN"
        assert _jobs() == before
        audit = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "approval.expired",
                AuditLog.resource_id == str(approval_id),
            )
        )
        assert audit is not None


def test_viewer_cannot_approve(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server_id = _server("APP01").id
    approval_id = _approval_id(_post_action(client, server_id, "restart_docker_service", "Docker"))
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "viewer")
    denied = post_csrf(
        client,
        f"/automation/approvals/{approval_id}/approve",
        {},
        page="/automation/approvals",
    )
    assert denied.status_code == 403
    assert b"Permission denied for Viewer role" in denied.data


def test_direct_dispatch_cannot_skip_approval(seeded):
    from app.services.approval import ApprovalPending
    from app.services.automation import queue_and_dispatch

    with seeded.app_context():
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        server = _server("APP01")
        before = _jobs()
        try:
            queue_and_dispatch(
                server_id=server.id,
                action_key="restart_docker_service",
                parameters={},
                actor=operator,
            )
        except ApprovalPending as pending:
            assert pending.request.status == "PENDING_APPROVAL"
            assert pending.request.job_id is None
        else:
            raise AssertionError("direct dispatch must stop for approval")
        assert _jobs() == before


def test_audit_log_filters_by_date(seeded, client):
    login(client, "admin")
    empty = client.get("/audit/?from=2099-01-01&to=2099-01-02")
    assert b"No audit records for this filter." in empty.data
    visible = client.get("/audit/?from=2020-01-01&to=2099-01-01")
    assert b"No audit records for this filter." not in visible.data
    assert b"audit-from" in visible.data
