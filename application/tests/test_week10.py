"""Week 10 incident lifecycle, recovery status, and approval linkage."""

from sqlalchemy import func, select

from app.executors.actions import ACTIONS, FAILURE_PLAYBOOKS, playbook_for
from app.executors.ansible import _playbook_timeout, playbook_failure_stage
from app.extensions import db
from app.models import Alert, ApprovalRequest, AutomationJob, Incident, IncidentEvent, Server
from app.services.checks import verify_recovery
from app.services.incidents import IncidentTransitionError, acknowledge
from app.services.probes import http_recovery
from app.services.remediation import _open_manual_incident
from tests.conftest import login, post_csrf


def _server(name):
    return db.session.scalar(select(Server).where(Server.name == name))


def test_production_playbooks_and_timeouts_stay_on_the_lab_map(app):
    with app.app_context():
        expected = {
            ("WEB01", "restart_nginx"): "restart-nginx.yml",
            ("APP01", "restart_container"): "restart-app-container.yml",
            ("WIN01", "restart_windows_exporter"): "restart-windows-exporter.yml",
            ("AZURE01", "restart_nginx"): "restart-azure-nginx.yml",
            ("APP01", "restart_docker_service"): "restart-docker-service.yml",
            ("AZURE01", "reboot_server"): "reboot-azure01.yml",
        }
        for (host, action), filename in expected.items():
            assert playbook_for(host, action).endswith(filename)
        used = {item.playbook.rsplit("/", 1)[-1] for item in ACTIONS.values()}
        assert set(FAILURE_PLAYBOOKS.values()).isdisjoint(used)
        assert _playbook_timeout({}, "restart_nginx") == 90
        assert _playbook_timeout({}, "reboot_server") == 420


def test_failure_playbooks_are_classified_by_task_not_exit_code():
    execution, _name = playbook_failure_stage("TASK [Restart nginx]\nfailed: [WEB01]\n")
    verification, _name = playbook_failure_stage(
        "TASK [Restart nginx]\nok: [WEB01]\nTASK [Wait for nginx HTTP]\nfailed: [WEB01]\n"
    )
    assert execution == "execution_failed"
    assert verification == "verification_failed"


def test_http_403_is_not_recovery(seeded, monkeypatch):
    monkeypatch.setattr(
        "app.services.probes.requests.get",
        lambda url, timeout=3, allow_redirects=True: type("Response", (), {"status_code": 403})(),
    )
    ok, detail = http_recovery("http://192.168.10.11/")
    assert ok is False
    assert "403" in detail
    monkeypatch.setattr(
        "app.services.checks.http_recovery",
        lambda url, timeout=3: (True, "HTTP 200 (12 ms)"),
    )
    with seeded.app_context():
        seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
        recovered, text = verify_recovery(_server("WEB01"), "restart_nginx")
        assert recovered is True
        assert "HTTP 200" in text


def test_active_incident_is_reused_until_it_is_closed(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server = _server("WEB01")
        first = _open_manual_incident(server, "restart_nginx", None)
        again = _open_manual_incident(server, "restart_nginx", None)
        assert again.id == first.id
        incident_id = first.id
        jobs_before = db.session.scalar(select(func.count()).select_from(AutomationJob))
    page = client.get(f"/incidents/{incident_id}")
    assert page.status_code == 200
    assert b"INC-" in page.data
    assert b"Incident Detected" in page.data
    acknowledged = post_csrf(client, f"/incidents/{incident_id}/acknowledge", {}, page=f"/incidents/{incident_id}")
    assert acknowledged.status_code == 302
    with seeded.app_context():
        row = db.session.get(Incident, incident_id)
        assert row.status == "acknowledged"
        assert row.acknowledged_at is not None
        assert row.acknowledger.username == "operator"
    post_csrf(client, "/logout", {}, page=f"/incidents/{incident_id}")
    login(client, "viewer")
    denied = post_csrf(client, f"/incidents/{incident_id}/acknowledge", {}, page=f"/incidents/{incident_id}")
    assert denied.status_code == 403
    post_csrf(client, "/logout", {}, page="/dashboard")
    login(client, "operator")
    refused = post_csrf(client, f"/incidents/{incident_id}/close", {}, page=f"/incidents/{incident_id}")
    assert refused.status_code == 302
    with seeded.app_context():
        row = db.session.get(Incident, incident_id)
        assert row.status == "acknowledged"
        from app.services.incidents import add_event

        add_event(row, "resolved", "Recovery confirmed", to_status="resolved")
        db.session.commit()
    closed = post_csrf(client, f"/incidents/{incident_id}/close", {}, page=f"/incidents/{incident_id}")
    assert closed.status_code == 302
    with seeded.app_context():
        row = db.session.get(Incident, incident_id)
        assert row.status == "closed"
        assert row.closed_by is not None
        fresh = _open_manual_incident(server, "restart_nginx", None)
        assert fresh.id != incident_id
        assert fresh.status == "open"
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == jobs_before
        with_events = db.session.scalars(
            select(IncidentEvent.event_key).where(IncidentEvent.incident_id == incident_id)
        ).all()
        assert "detected" in with_events
        assert "acknowledged" in with_events
        assert "closed" in with_events


def test_acknowledge_rejects_an_illegal_status(seeded):
    with seeded.app_context():
        incident = _open_manual_incident(_server("WEB01"), "restart_nginx", None)
        acknowledge(incident, None)
        db.session.commit()
        try:
            acknowledge(incident, None)
        except IncidentTransitionError:
            pass
        else:
            raise AssertionError("acknowledging twice should be rejected")


def test_incident_page_requests_approval_and_keeps_the_job_waiting(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        medium = _open_manual_incident(_server("APP01"), "restart_docker_service", None)
        high = _open_manual_incident(_server("AZURE01"), "reboot_server", None)
        medium_id = medium.id
        high_id = high.id
    page = client.get(f"/incidents/{medium_id}")
    assert page.status_code == 200
    assert b"MEDIUM" in page.data
    assert b"Restart Docker" in page.data
    assert b"Docker service down" in page.data
    assert b"restart_container" in page.data
    assert b"restart_docker_service" in page.data
    assert b'name="action_key"' in page.data
    assert b"Request Approval" in page.data
    assert b"restart-docker-service" in page.data
    assert b">View Runbook</a>" in page.data
    assert b"1. Incident" not in page.data
    assert b"close-incident" not in page.data
    requested = post_csrf(client, f"/incidents/{medium_id}/remediate", {}, page=f"/incidents/{medium_id}")
    assert requested.status_code == 302
    assert requested.headers["Location"].endswith(f"/incidents/{medium_id}")
    with seeded.app_context():
        approval = db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.incident_id == medium_id))
        assert approval.status == "PENDING_APPROVAL"
        assert approval.risk == "MEDIUM"
        assert approval.job_id is None
        assert db.session.scalar(
            select(func.count()).select_from(AutomationJob).where(AutomationJob.incident_id == medium_id)
        ) == 0
        events = db.session.scalars(
            select(IncidentEvent.event_key).where(IncidentEvent.incident_id == medium_id)
        ).all()
        assert "approval_requested" in events
    waiting = client.get(f"/incidents/{medium_id}")
    assert b"PENDING_APPROVAL" in waiting.data
    assert b"Request Approval" not in waiting.data
    high_page = client.get(f"/incidents/{high_id}")
    assert b"HIGH" in high_page.data
    assert b"restart_nginx" in high_page.data
    assert b"reboot_server" in high_page.data
    assert b"Only an admin can request this HIGH action." in high_page.data
    denied = post_csrf(client, f"/incidents/{high_id}/remediate", {}, page=f"/incidents/{high_id}")
    assert denied.status_code == 403
    with seeded.app_context():
        assert db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.incident_id == high_id)) is None


def test_incident_detail_preselects_container_or_docker_from_the_cause(seeded, client):
    from app.models import utcnow

    login(client, "operator")
    now = utcnow()
    with seeded.app_context():
        server = _server("APP01")
        alert = Alert(
            server_id=server.id,
            fingerprint="fp-incident-container-choice",
            alert_name="container_down",
            severity="critical",
            status="firing",
            summary="container_down",
            starts_at=now,
            created_at=now,
        )
        db.session.add(alert)
        db.session.commit()
        incident = _open_manual_incident(server, "restart_container", alert.id)
        incident_id = incident.id
    container_page = client.get(f"/incidents/{incident_id}")
    assert b"Container down" in container_page.data
    assert b'value="restart_container"' in container_page.data
    assert b'value="restart_docker_service"' in container_page.data
    assert b"Run remediation" in container_page.data
    assert b"Request Approval" not in container_page.data
    with seeded.app_context():
        docker = Alert(
            server_id=_server("APP01").id,
            fingerprint="fp-incident-docker-choice",
            alert_name="Docker Service Down",
            severity="critical",
            status="firing",
            summary="Docker Service Down",
            starts_at=now,
            created_at=now,
        )
        db.session.add(docker)
        db.session.commit()
    docker_page = client.get(f"/incidents/{incident_id}")
    assert b"Docker service down" in docker_page.data
    assert b"Request Approval" in docker_page.data
    posted = post_csrf(
        client,
        f"/incidents/{incident_id}/remediate",
        {"action_key": "restart_container"},
        page=f"/incidents/{incident_id}",
    )
    assert posted.status_code == 302
    with seeded.app_context():
        approval = db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.incident_id == incident_id))
        assert approval.action_key == "restart_docker_service"
        assert approval.risk == "MEDIUM"
        assert approval.job_id is None
        assert (
            db.session.scalar(select(func.count()).select_from(AutomationJob).where(AutomationJob.incident_id == incident_id))
            == 0
        )


def test_medium_approval_links_one_incident_and_one_job(seeded, client, monkeypatch):
    from app.executors.base import ExecutionResult
    from app.models import utcnow

    def ok(self, job, server, action):
        now = utcnow()
        return ExecutionResult(True, 0, "restarted", now, now)

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", ok)
    login(client, "operator")
    with seeded.app_context():
        server_id = _server("APP01").id
    requested = post_csrf(
        client,
        "/automation/jobs",
        {
            "server_id": str(server_id),
            "action_key": "restart_docker_service",
            "service": "Docker",
            "mode": "MANUAL",
            "simulate": "success",
            "submit": "Trigger remediation",
        },
        page="/automation/",
    )
    assert requested.status_code == 302
    with seeded.app_context():
        approval = db.session.scalar(select(ApprovalRequest).order_by(ApprovalRequest.id.desc()))
        assert approval.incident_id is not None
        assert approval.job_id is None
        assert (
            db.session.scalar(
                select(func.count()).select_from(AutomationJob).where(AutomationJob.incident_id == approval.incident_id)
            )
            == 0
        )
        incident_id = approval.incident_id
        request_id = approval.id
    post_csrf(client, "/logout", {}, page="/automation/")
    login(client, "admin")
    approved = post_csrf(
        client,
        f"/automation/approvals/{request_id}/approve",
        {},
        page=f"/automation/approvals/{request_id}",
    )
    assert approved.status_code == 302
    with seeded.app_context():
        approval = db.session.get(ApprovalRequest, request_id)
        jobs = db.session.scalars(select(AutomationJob).where(AutomationJob.incident_id == incident_id)).all()
        assert approval.job_id is not None
        assert len(jobs) == 1
        assert jobs[0].id == approval.job_id
        assert jobs[0].incident_id == incident_id


def test_known_cause_selects_the_runbook_and_an_unknown_cause_does_not_run(seeded):
    from app.models import utcnow
    from app.services.remediation import maybe_remediate

    seeded.config["AUTO_REMEDIATION_ENABLED"] = True
    now = utcnow()
    with seeded.app_context():
        server = _server("APP01")
        docker = Alert(
            server_id=server.id,
            fingerprint="fp-docker-cause",
            alert_name="Docker Service Down",
            severity="critical",
            status="firing",
            summary="Docker Service Down",
            starts_at=now,
            created_at=now,
        )
        vague = Alert(
            server_id=server.id,
            fingerprint="fp-unknown-cause",
            alert_name="service_down",
            severity="critical",
            status="firing",
            summary="service_down",
            starts_at=now,
            created_at=now,
        )
        db.session.add_all((docker, vague))
        db.session.commit()
        assert maybe_remediate(docker) is None
        approval = db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.alert_id == docker.id))
        assert approval.action_key == "restart_docker_service"
        assert approval.risk == "MEDIUM"
        assert approval.job_id is None
        linked = db.session.get(Incident, approval.incident_id)
        assert linked.action_key == "restart_docker_service"
        assert linked.status == "open"
        assert maybe_remediate(vague) is None
        assert (
            db.session.scalar(select(func.count()).select_from(AutomationJob).where(AutomationJob.alert_id == vague.id))
            == 0
        )
        investigation = db.session.scalar(select(Incident).where(Incident.alert_id == vague.id))
        assert investigation.action_key == "investigate"
        assert investigation.status == "open"
        assert investigation.manual_required is True
        assert db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.alert_id == vague.id)) is None


def test_runbook_map_prechecks_every_target(seeded):
    from app.models import utcnow
    from app.services.remediation import maybe_remediate
    from app.services.runbooks import RUNBOOK_MAP, classify_incident

    seeded.config["AUTO_REMEDIATION_ENABLED"] = True
    with seeded.app_context():
        for row in RUNBOOK_MAP:
            plan = classify_incident(row["host"], row["incident_type"])
            assert plan["action_key"] == row["action"]
            assert plan["incident_type"] == row["incident_type"]
        assert classify_incident("AZURE01", "InstanceDown")["incident_type"] == "unknown_issue"
        assert classify_incident("AZURE01", "nginx_down")["action_key"] == "restart_nginx"
        assert classify_incident("APP01", "container_down", docker_active=False)["action_key"] == "restart_docker_service"
        assert classify_incident("WEB01", "nginx_down", management_down=True)["incident_type"] == "management_unavailable"
        server = _server("APP01")
        now = utcnow()
        alert = Alert(
            server_id=server.id,
            fingerprint="fp-container-docker-down",
            alert_name="container_down",
            severity="critical",
            status="firing",
            summary="container_down",
            starts_at=now,
            created_at=now,
        )
        db.session.add(alert)
        db.session.commit()
        seeded.config["DOCKER_ACTIVE_CHECK"] = lambda _server: False
        assert maybe_remediate(alert) is None
        assert (
            db.session.scalar(select(func.count()).select_from(AutomationJob).where(AutomationJob.alert_id == alert.id))
            == 0
        )
        approval = db.session.scalar(select(ApprovalRequest).where(ApprovalRequest.alert_id == alert.id))
        assert approval.action_key == "restart_docker_service"
        assert approval.job_id is None
        assert approval.risk == "MEDIUM"
