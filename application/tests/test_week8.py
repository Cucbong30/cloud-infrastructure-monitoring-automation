"""Week 8: manual remediation stays on the existing policy and RBAC."""

from sqlalchemy import func, select

from app.extensions import db
from app.models import AuditLog, AutomationJob, Server, User, utcnow
from tests.conftest import login, post_csrf


def _server(name="WEB01"):
    return db.session.scalar(select(Server).where(Server.name == name))


def _post_manual(client, server_id, simulate="success"):
    return post_csrf(
        client,
        "/automation/jobs",
        {
            "server_id": str(server_id),
            "action_key": "restart_nginx",
            "service": "Nginx",
            "mode": "MANUAL",
            "simulate": simulate,
            "submit": "Trigger remediation",
        },
        page="/automation/",
    )


def test_viewer_cannot_trigger_and_the_denial_is_audited(seeded, client):
    login(client, "viewer")
    page = client.get("/automation/")
    assert b'id="execute-button"' not in page.data
    assert b"not available for this role" in page.data
    with seeded.app_context():
        server_id = _server().id
    denied = _post_manual(client, server_id)
    assert denied.status_code == 403
    assert b"403 Forbidden" in denied.data
    assert b"Permission denied for Viewer role" in denied.data
    with seeded.app_context():
        entry = db.session.scalar(select(AuditLog).where(AuditLog.action == "permission.denied"))
        assert entry is not None
        assert '"result": "DENIED"' in entry.details_json
        assert "Permission denied for Viewer role" in entry.details_json
        assert "MANUAL" in entry.details_json


def test_admin_and_operator_see_the_manual_form(seeded, client):
    for username in ("admin", "operator"):
        login(client, username)
        page = client.get("/automation/")
        assert page.status_code == 200
        assert b"Manual remediation" in page.data
        assert b"Trigger remediation" in page.data
        assert b'value="MANUAL"' in page.data
        post_csrf(client, "/logout", {}, page="/dashboard")


def test_manual_success_records_mode_actor_and_info_mail(seeded, client):
    sent = []

    def capture(event, fields, recipients):
        sent.append((event, fields, recipients))

    seeded.config["NOTIFY_TRANSPORT"] = capture
    seeded.config["ALERT_RECIPIENT_INFO"] = "KLTN-Alert-Info@cucbong.id.vn"
    login(client, "operator")
    with seeded.app_context():
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        operator.email = "operator01@cucbong.id.vn"
        db.session.commit()
        server_id = _server().id
    response = _post_manual(client, server_id)
    assert response.status_code == 302
    with seeded.app_context():
        job = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert job.mode == "MANUAL"
        assert job.trigger_source == "manual"
        assert job.final_status == "SUCCESS"
        assert job.status == "succeeded"
        assert job.triggered_by == "operator01@cucbong.id.vn"
        assert job.user_email == "operator01@cucbong.id.vn"
        assert job.user_role == "operator"
        assert job.incident_id is not None
        verified = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "remediation.verified",
                AuditLog.resource_id == str(job.id),
            )
        )
        assert '"mode": "MANUAL"' in verified.details_json
        assert "operator01@cucbong.id.vn" in verified.details_json
        assert '"final_status": "SUCCESS"' in verified.details_json
        job_id = job.id
    assert sent
    assert sent[-1][0] == "remediation_success"
    assert sent[-1][1]["mode"] == "MANUAL"
    assert sent[-1][1]["triggered_by"] == "operator01@cucbong.id.vn"
    detail = client.get(f"/automation/jobs/{job_id}")
    assert b"MANUAL" in detail.data
    assert b"operator01@cucbong.id.vn" in detail.data
    assert b"SUCCESS" in detail.data


def test_active_job_skips_the_duplicate_without_running(seeded, client, monkeypatch):
    calls = {"count": 0}

    def explode(self, job, server, action):
        calls["count"] += 1
        raise AssertionError("duplicate request must not execute")

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", explode)
    login(client, "operator")
    with seeded.app_context():
        server = _server()
        active = AutomationJob(
            server_id=server.id,
            requested_by=None,
            trigger_source="auto",
            executor="mock",
            action_key="restart_nginx",
            parameters_json="{}",
            status="queued",
            mode="AUTO",
            triggered_by="SYSTEM",
            user_role="SYSTEM",
            created_at=utcnow(),
        )
        db.session.add(active)
        db.session.commit()
        server_id = server.id
        active_id = active.id
    response = _post_manual(client, server_id)
    assert response.status_code == 302
    assert calls["count"] == 0
    with seeded.app_context():
        skipped = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert skipped.id != active_id
        assert skipped.status == "canceled"
        assert skipped.final_status == "DUPLICATE_SKIPPED"
        assert skipped.mode == "MANUAL"
        assert skipped.reason == "An active remediation job already exists for this target and action."
        assert db.session.get(AutomationJob, active_id).status == "queued"
    page = client.get(response.headers["Location"])
    assert b"DUPLICATE_SKIPPED" in page.data
    assert b'id="duplicate-drawer"' in page.data
    assert b"An active remediation job already exists for this target and action." in page.data


def test_manual_verification_failure_does_not_retry(seeded, client):
    seeded.config["RECOVERY_CHECK"] = lambda server, action: (False, "Nginx :80 did not respond.")
    login(client, "admin")
    with seeded.app_context():
        server_id = _server().id
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
    response = _post_manual(client, server_id)
    assert response.status_code == 302
    with seeded.app_context():
        after = db.session.scalar(select(func.count()).select_from(AutomationJob))
        job = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert after == before + 1
        assert job.final_status == "VERIFICATION_FAILED"
        assert job.verification_result == "failed"
        assert job.mode == "MANUAL"
        assert job.user_role == "admin"
    page = client.get(response.headers["Location"])
    assert b"Execution: SUCCESS" in page.data
    assert b"Verification: FAILED" in page.data
    assert b"Retry: NO" in page.data
    assert b"VERIFICATION_FAILED" in page.data
    assert b"View Runbook: nginx-verification-failed" in page.data


def test_manual_failure_blocked_and_retry_mails(seeded, client):
    sent = []

    def capture(event, fields, recipients):
        sent.append((event, fields, recipients))

    seeded.config["NOTIFY_TRANSPORT"] = capture
    seeded.config["ALERT_RECIPIENT_CRITICAL"] = "KLTN-Alert-Critical@cucbong.id.vn"
    seeded.config["ALERT_RECIPIENT_WARNING"] = "KLTN-Alert-Warning@cucbong.id.vn"
    login(client, "operator")
    with seeded.app_context():
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        operator.email = "operator01@cucbong.id.vn"
        db.session.commit()
        server_id = _server().id
    failed = _post_manual(client, server_id, simulate="fail")
    assert failed.status_code == 302
    execution = [item for item in sent if item[0] == "execution_failed"]
    assert execution
    assert execution[-1][1]["mode"] == "MANUAL"
    assert execution[-1][1]["triggered_by"] == "operator01@cucbong.id.vn"
    assert execution[-1][1]["status"] == "EXECUTION_FAILED"
    assert execution[-1][1]["execution_result"] == "FAILED"
    job_url = failed.headers["Location"]
    sent.clear()
    retried = post_csrf(client, job_url + "/retry", {}, page=job_url)
    assert retried.status_code == 302
    assert any(item[0] == "retry" and item[1]["mode"] == "MANUAL" for item in sent)
    sent.clear()
    seeded.config["MANAGEMENT_CHECK"] = lambda server: "SSH :22 is down."
    blocked = _post_manual(client, server_id)
    assert blocked.status_code == 302
    blocked_mail = [item for item in sent if item[0] == "blocked"]
    assert blocked_mail
    assert blocked_mail[-1][1]["mode"] == "MANUAL"
    assert blocked_mail[-1][1]["status"] == "MANAGEMENT_BLOCKED"
    assert blocked_mail[-1][1]["execution_result"] == "NOT_RUN"


def test_manual_execution_failure_does_not_retry(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server_id = _server().id
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
    response = _post_manual(client, server_id, simulate="fail")
    assert response.status_code == 302
    with seeded.app_context():
        after = db.session.scalar(select(func.count()).select_from(AutomationJob))
        job = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert after == before + 1
        assert job.final_status == "EXECUTION_FAILED"
        assert job.verification_result == "skipped"
    page = client.get(response.headers["Location"])
    assert b"Execution: FAILED" in page.data
    assert b"Retry: NO" in page.data
    assert b"EXECUTION_FAILED" in page.data
    assert b"View Runbook: nginx-execution-failed" in page.data


def test_manual_management_block_does_not_run_the_playbook(seeded, client, monkeypatch):
    calls = {"count": 0}

    def explode(self, job, server, action):
        calls["count"] += 1
        raise AssertionError("blocked request must not execute")

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", explode)
    seeded.config["MANAGEMENT_CHECK"] = lambda server: "SSH :22 is down."
    login(client, "operator")
    with seeded.app_context():
        server_id = _server().id
    response = _post_manual(client, server_id)
    assert response.status_code == 302
    assert calls["count"] == 0
    with seeded.app_context():
        job = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert job.final_status == "MANAGEMENT_BLOCKED"
        assert job.verification_result == "blocked"
        assert job.mode == "MANUAL"
    page = client.get(response.headers["Location"])
    assert b"MANAGEMENT_BLOCKED" in page.data
    assert b"Execution: NOT_RUN" in page.data
    assert b"View Runbook: nginx-management-blocked" in page.data


def test_auto_audit_keeps_system_actor(seeded):
    from tests.test_auto_remediation import FakePrometheus, _alert, _enable
    from app.services.alert_sync import sync_alerts
    from app.services.inventory_sync import sync_inventory

    _enable(seeded)
    with seeded.app_context():
        sync_inventory()
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-week8-auto", "192.168.10.11:9100")]))
        job = db.session.scalar(select(AutomationJob).where(AutomationJob.trigger_source == "auto").order_by(AutomationJob.id.desc()))
        assert job.mode == "AUTO"
        assert job.triggered_by == "SYSTEM"
        assert job.user_role == "SYSTEM"
        verified = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "auto_remediation.verified",
                AuditLog.resource_id == str(job.id),
            )
        )
        assert '"mode": "AUTO"' in verified.details_json
        assert '"triggered_by": "SYSTEM"' in verified.details_json
