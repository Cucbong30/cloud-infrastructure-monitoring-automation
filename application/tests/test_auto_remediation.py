import threading
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.extensions import db
from app.models import Alert, AuditLog, AutomationJob, Incident, Server
from app.services.alert_sync import sync_alerts
from app.services.automation import enqueue_job
from app.services.prometheus import PrometheusAlert
from app.services.remediation import maybe_remediate, schedule_auto_remediation
from tests.conftest import csrf_from, login
from tests.test_alert_sync import FakePrometheus


def _alert(name, fingerprint, instance):
    return PrometheusAlert(
        fingerprint=fingerprint,
        alert_name=name,
        severity="critical",
        category="availability",
        summary=name,
        description="detail",
        state="firing",
        starts_at=datetime(2026, 11, 2, 12, tzinfo=timezone.utc),
        labels={"instance": instance, "alertname": name},
        instance=instance,
    )


def _enable(app):
    app.config["AUTO_REMEDIATION_ENABLED"] = True
    app.config["AUTO_REMEDIATION_COOLDOWN_SECONDS"] = 300
    app.config["AUTO_REMEDIATION_MAX_RETRIES"] = 1


def test_auto_maps_each_allow_listed_host(seeded):
    _enable(seeded)
    cases = [
        ("NginxDown", "fp-web", "192.168.10.11:9100", "restart_nginx"),
        ("service_down", "fp-app", "192.168.10.12:9100", "restart_container"),
        ("WindowsExporterDown", "fp-win", "192.168.10.13:9182", "restart_windows_exporter"),
    ]
    with seeded.app_context():
        for name, fingerprint, instance, action in cases:
            result = sync_alerts(FakePrometheus([_alert(name, fingerprint, instance)]))
            assert result.remediated == 1
            alert = db.session.scalar(select(Alert).where(Alert.fingerprint == fingerprint))
            job = db.session.scalar(select(AutomationJob).where(AutomationJob.alert_id == alert.id))
            assert job.action_key == action
            assert job.trigger_source == "auto"
            assert job.status == "succeeded"
            assert job.verification_result == "passed"
            started = db.session.scalar(
                select(AuditLog).where(AuditLog.action == "auto_remediation.started", AuditLog.resource_id == str(job.id))
            )
            assert started is not None


def test_repeat_firing_during_cooldown_does_not_create_a_job(seeded):
    _enable(seeded)
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-cool", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-cool"))
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        assert maybe_remediate(alert) is None
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert skipped is not None
        assert "Cooldown" in skipped.details_json


def test_queued_action_blocks_a_duplicate_auto_job(seeded):
    _enable(seeded)
    with seeded.app_context():
        seeded.config["AUTO_REMEDIATION_ENABLED"] = False
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-dup", "192.168.10.11:9100")]))
        seeded.config["AUTO_REMEDIATION_ENABLED"] = True
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-dup"))
        server = db.session.get(Server, alert.server_id)
        enqueue_job(
            server_id=server.id,
            action_key="restart_nginx",
            parameters={},
            trigger_source="manual",
            alert_id=alert.id,
        )
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        assert maybe_remediate(alert) is None
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert "already queued or running" in skipped.details_json


def test_management_down_blocks_without_a_playbook(seeded):
    _enable(seeded)
    seeded.config["MANAGEMENT_CHECK"] = lambda server: "WEB01 management channel SSH :22 is down"
    with seeded.app_context():
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-down", "192.168.10.11:9100")]))
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-down"))
        actions = {
            row.action
            for row in db.session.scalars(select(AuditLog).where(AuditLog.resource_id == str(alert.id))).all()
        }
        assert "auto_remediation.blocked" in actions
        assert "manual_intervention.required" in actions
        assert "auto_remediation.started" not in actions


def test_verification_failure_does_not_retry(seeded):
    _enable(seeded)
    seeded.config["RECOVERY_CHECK"] = lambda server, action: (False, "App :8080 is down.")
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("service_down", "fp-verify", "192.168.10.12:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-verify"))
        jobs = db.session.scalars(
            select(AutomationJob).where(AutomationJob.alert_id == alert.id).order_by(AutomationJob.id)
        ).all()
        assert len(jobs) == 1
        assert jobs[0].exit_code == 0
        assert jobs[0].status == "failed"
        assert jobs[0].verification_result == "failed"
        assert maybe_remediate(alert) is None
        assert db.session.scalar(select(func.count()).select_from(AutomationJob).where(AutomationJob.alert_id == alert.id)) == 1
        manual = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "manual_intervention.required",
                AuditLog.resource_id == str(alert.id),
            )
        )
        assert manual is not None
        assert "verification failed" in manual.details_json
        assert "MANUAL_REQUIRED" in manual.details_json


def test_execution_failure_retries_once_then_asks_for_manual(seeded, monkeypatch):
    _enable(seeded)

    def fail(self, job, server, action):
        from app.executors.base import ExecutionResult
        from app.models import utcnow

        now = utcnow()
        return ExecutionResult(False, 2, "command failed", now, now)

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", fail)
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-exec", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-exec"))
        jobs = db.session.scalars(
            select(AutomationJob).where(AutomationJob.alert_id == alert.id).order_by(AutomationJob.id)
        ).all()
        assert len(jobs) == 2
        assert jobs[0].verification_result == "skipped"
        assert jobs[0].exit_code == 2
        assert jobs[1].retry_of_job_id == jobs[0].id
        assert jobs[1].verification_result == "skipped"
        assert maybe_remediate(alert) is None
        manual = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "manual_intervention.required",
                AuditLog.resource_id == str(alert.id),
            )
        )
        assert "retry limit" in manual.details_json
        assert "MANUAL_REQUIRED" in manual.details_json


def test_capacity_alert_stays_diagnostic(seeded):
    _enable(seeded)
    with seeded.app_context():
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        sync_alerts(FakePrometheus([_alert("disk_high", "fp-disk", "192.168.10.11:9100")]))
        sync_alerts(FakePrometheus([_alert("cpu_high", "fp-cpu", "192.168.10.12:9100")]))
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-disk"))
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert "diagnostic" in skipped.details_json
        assert (
            db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "manual_intervention.required",
                    AuditLog.resource_id == str(alert.id),
                )
            )
            is None
        )


def test_unknown_action_does_not_auto_run(seeded):
    _enable(seeded)
    with seeded.app_context():
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        sync_alerts(FakePrometheus([_alert("certificate_expired", "fp-unknown", "192.168.10.11:9100")]))
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-unknown"))
        manual = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "manual_intervention.required",
                AuditLog.resource_id == str(alert.id),
            )
        )
        assert "no allow-listed" in manual.details_json


def test_maintenance_still_stores_the_alert_and_skips_auto(seeded):
    _enable(seeded)
    seeded.config["MANAGEMENT_CHECK"] = lambda server: "WEB01 management channel SSH :22 is down"
    with seeded.app_context():
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        server.status = "maintenance"
        db.session.commit()
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-maint", "192.168.10.11:9100")]))
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-maint"))
        assert alert.status == "firing"
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert "maintenance" in skipped.details_json
        assert "auto_remediation.blocked" not in {
            row.action for row in db.session.scalars(select(AuditLog).where(AuditLog.resource_id == str(alert.id)))
        }
        assert db.session.get(Server, server.id).status == "maintenance"


def test_capacity_alert_stays_diagnostic_when_ssh_is_down(seeded):
    _enable(seeded)
    seeded.config["MANAGEMENT_CHECK"] = lambda server: "WEB01 management channel SSH :22 is down"
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("memory_high", "fp-mem", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-mem"))
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert "diagnostic" in skipped.details_json


def test_cooldown_is_reported_before_a_duplicate(seeded):
    _enable(seeded)
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-order", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-order"))
        server = db.session.get(Server, alert.server_id)
        enqueue_job(
            server_id=server.id,
            action_key="restart_nginx",
            parameters={},
            trigger_source="manual",
            alert_id=alert.id,
        )
        assert maybe_remediate(alert) is None
        skipped = db.session.scalar(
            select(AuditLog)
            .where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
            .order_by(AuditLog.id.desc())
        )
        assert "Cooldown" in skipped.details_json


def test_live_probe_keeps_maintenance(seeded):
    from app.services.metrics import _apply_live_status

    with seeded.app_context():
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        server.status = "maintenance"
        db.session.commit()
        _apply_live_status([{"name": "WEB01", "status": "Degraded"}])
        db.session.refresh(server)
        assert server.status == "maintenance"
        assert server.last_seen_at is not None


def test_risky_actions_are_rejected():
    from app.services.automation import AutomationRejected, validate_parameters

    for key in ("reboot", "kill_process", "disk_cleanup", "delete_file", "network_change"):
        try:
            validate_parameters(key, {})
        except AutomationRejected as exc:
            assert "diagnostic only" in str(exc)
        else:
            raise AssertionError(key)


def test_dashboard_considers_a_firing_alert_again(seeded, monkeypatch):
    seeded.config["AUTO_REMEDIATION_ENABLED"] = False
    done = threading.Event()
    seen = []

    def fake(alert):
        seen.append(alert.id)
        done.set()
        return None

    monkeypatch.setattr("app.services.remediation.maybe_remediate", fake)
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-again", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-again"))
        seeded.config["AUTO_REMEDIATION_ENABLED"] = True
        schedule_auto_remediation([alert])
        assert done.wait(2)
        assert seen == [alert.id]


def test_old_blocked_retry_does_not_consume_a_new_failure(seeded):
    from app.models import Incident

    _enable(seeded)
    seeded.config["AUTO_REMEDIATION_COOLDOWN_SECONDS"] = 0
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-fresh", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-fresh"))
        succeeded = db.session.scalar(select(AutomationJob).where(AutomationJob.alert_id == alert.id))
        blocked = enqueue_job(
            server_id=succeeded.server_id,
            action_key="restart_nginx",
            parameters={},
            trigger_source="remediation",
            alert_id=alert.id,
            retry_of_job_id=succeeded.id,
        )
        blocked.status = "failed"
        blocked.verification_result = "blocked"
        failed = enqueue_job(
            server_id=succeeded.server_id,
            action_key="restart_nginx",
            parameters={},
            trigger_source="auto",
            alert_id=alert.id,
        )
        failed.status = "failed"
        failed.verification_result = "skipped"
        failed.verification_detail = "Playbook failed before verification."
        db.session.commit()
        retried = maybe_remediate(alert)
        assert retried is not None
        assert retried.retry_of_job_id is None
        assert retried.attempt == 1
        assert retried.id != blocked.id
        assert retried.id != failed.id
        incident = db.session.get(Incident, retried.incident_id)
        assert incident.retry_count == 0
        assert incident.manual_required is False


def test_new_incident_starts_at_zero_after_manual_required(seeded, monkeypatch):
    from app.executors.base import ExecutionResult
    from app.models import utcnow

    _enable(seeded)
    seeded.config["AUTO_REMEDIATION_COOLDOWN_SECONDS"] = 0

    def fail(self, job, server, action):
        now = utcnow()
        return ExecutionResult(False, 2, "command failed", now, now)

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", fail)
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-reset", "192.168.10.11:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-reset"))
        first = db.session.scalar(select(Incident).where(Incident.alert_id == alert.id, Incident.status == "open"))
        assert first.retry_count == 1
        assert first.reason == "retry_limit"
        assert first.manual_required is True
        assert maybe_remediate(alert) is None

        seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
        seeded.config["RECOVERY_CHECK"] = lambda server, action: (True, "Nginx :80 is up (20 ms).")
        assert maybe_remediate(alert) is None
        db.session.refresh(first)
        assert first.status == "resolved"

        seeded.config["AUTOMATION_EXECUTOR"] = "mock"
        seeded.config.pop("RECOVERY_CHECK", None)

        def ok(self, job, server, action):
            now = utcnow()
            return ExecutionResult(True, 0, "restarted", now, now)

        monkeypatch.setattr("app.executors.mock.MockExecutor.execute", ok)
        fresh = maybe_remediate(alert)
        assert fresh is not None
        assert fresh.attempt == 1
        assert fresh.retry_of_job_id is None
        assert fresh.final_status == "SUCCESS"
        assert fresh.incident_id != first.id
        second = db.session.get(Incident, fresh.incident_id)
        assert second.retry_count == 0
        assert second.manual_required is False
        assert second.verification_failed is False
        assert second.blocked is False
        assert second.status == "resolved"


def test_healthy_service_is_not_marked_manual(seeded):
    _enable(seeded)
    seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
    seeded.config["RECOVERY_CHECK"] = lambda server, action: (True, "Nginx :80 is up (20 ms).")
    with seeded.app_context():
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-up", "192.168.10.11:9100")]))
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-up"))
        skipped = db.session.scalar(
            select(AuditLog).where(AuditLog.action == "auto_remediation.skipped", AuditLog.resource_id == str(alert.id))
        )
        assert "service is up" in skipped.details_json
        manual = db.session.scalar(
            select(AuditLog).where(
                AuditLog.action == "manual_intervention.required",
                AuditLog.resource_id == str(alert.id),
            )
        )
        assert manual is None


def test_operator_click_stays_manual(seeded, client):
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("NginxDown", "fp-manual", "192.168.10.11:9100")]))
        alert_id = db.session.scalar(select(Alert.id).where(Alert.fingerprint == "fp-manual"))
    login(client, "operator")
    with seeded.app_context():
        server = db.session.get(Server, db.session.get(Alert, alert_id).server_id)
        server.status = "warning"
        db.session.commit()
    token = csrf_from(client.get("/alerts/"))
    response = client.post(f"/alerts/{alert_id}/remediate", data={"csrf_token": token})
    assert response.status_code == 302
    assert "/automation/jobs/" in response.headers.get("Location", "")
    with seeded.app_context():
        job = db.session.scalar(select(AutomationJob).where(AutomationJob.alert_id == alert_id))
        assert job.trigger_source == "manual"
        assert job.status == "succeeded"


_TARGETS = (
    ("NginxDown", "192.168.10.11:9100", "restart_nginx", "WEB01"),
    ("service_down", "192.168.10.12:9100", "restart_container", "APP01"),
    ("WindowsExporterDown", "192.168.10.13:9182", "restart_windows_exporter", "WIN01"),
)


def test_production_playbooks_stay_on_the_lab_targets():
    from app.executors.actions import ACTIONS

    assert ACTIONS["restart_nginx"].playbook == "~/ansible/playbooks/restart-nginx.yml"
    assert ACTIONS["restart_container"].playbook == "~/ansible/playbooks/restart-app-container.yml"
    assert ACTIONS["restart_windows_exporter"].playbook == "~/ansible/playbooks/restart-windows-exporter.yml"
    assert ACTIONS["restart_nginx"].risk == "low"
    assert ACTIONS["restart_container"].risk == "low"
    assert ACTIONS["restart_windows_exporter"].risk == "low"


def test_each_target_auto_success_records_the_audit(seeded):
    from app.presentation import job_outcome_label

    _enable(seeded)
    with seeded.app_context():
        for name, instance, action, host in _TARGETS:
            sync_alerts(FakePrometheus([_alert(name, f"fp-ok-{host}", instance)]))
            alert = db.session.scalar(select(Alert).where(Alert.fingerprint == f"fp-ok-{host}"))
            job = db.session.scalar(select(AutomationJob).where(AutomationJob.alert_id == alert.id))
            assert job.action_key == action
            assert job.trigger_source == "auto"
            assert job_outcome_label(job) == "SUCCESS"
            verified = db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "auto_remediation.verified",
                    AuditLog.resource_id == str(job.id),
                )
            )
            assert f'"target": "{host}"' in verified.details_json
            assert f'"action": "{action}"' in verified.details_json
            assert '"trigger": "auto"' in verified.details_json
            assert '"result": "SUCCESS"' in verified.details_json


def test_each_target_execution_failure_ends_manual(seeded, monkeypatch):
    from app.executors.base import ExecutionResult
    from app.models import utcnow
    from app.presentation import job_outcome_label

    _enable(seeded)

    def fail(self, job, server, action):
        now = utcnow()
        return ExecutionResult(False, 2, "command failed", now, now)

    monkeypatch.setattr("app.executors.mock.MockExecutor.execute", fail)
    with seeded.app_context():
        for name, instance, action, host in _TARGETS:
            sync_alerts(FakePrometheus([_alert(name, f"fp-exec-{host}", instance)]))
            alert = db.session.scalar(select(Alert).where(Alert.fingerprint == f"fp-exec-{host}"))
            jobs = db.session.scalars(
                select(AutomationJob).where(AutomationJob.alert_id == alert.id).order_by(AutomationJob.id)
            ).all()
            assert len(jobs) == 2
            assert jobs[0].incident_id == jobs[1].incident_id
            assert jobs[0].attempt == 1
            assert jobs[0].final_status == "EXECUTION_FAILED"
            assert jobs[1].attempt == 2
            assert jobs[1].retry_of_job_id == jobs[0].id
            assert jobs[1].action_key == action
            assert jobs[1].reason == "retry_limit"
            assert job_outcome_label(jobs[1]) == "MANUAL_REQUIRED"
            incident = db.session.get(Incident, jobs[1].incident_id)
            assert incident.retry_count == 1
            assert incident.manual_required is True
            assert maybe_remediate(alert) is None


def test_each_target_blocks_before_the_playbook(seeded):
    _enable(seeded)
    seeded.config["MANAGEMENT_CHECK"] = lambda server: f"{server.name} management channel is down"
    with seeded.app_context():
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
        for name, instance, _action, host in _TARGETS:
            sync_alerts(FakePrometheus([_alert(name, f"fp-block-{host}", instance)]))
            alert = db.session.scalar(select(Alert).where(Alert.fingerprint == f"fp-block-{host}"))
            actions = {
                row.action
                for row in db.session.scalars(select(AuditLog).where(AuditLog.resource_id == str(alert.id))).all()
            }
            assert "auto_remediation.blocked" in actions
            assert "manual_intervention.required" in actions
            assert "auto_remediation.started" not in actions
            manual = db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "manual_intervention.required",
                    AuditLog.resource_id == str(alert.id),
                )
            )
            assert "BLOCKED" in manual.details_json
            assert '"result": "MANUAL_REQUIRED"' in manual.details_json
            assert f'"target": "{host}"' in manual.details_json
            incident = db.session.scalar(select(Incident).where(Incident.alert_id == alert.id))
            assert incident.blocked is True
            assert incident.manual_required is True
            assert incident.retry_count == 0
            assert incident.verification_failed is False
            assert incident.reason == "management_channel_unavailable"
            blocked = db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "auto_remediation.blocked",
                    AuditLog.resource_id == str(alert.id),
                )
            )
            assert '"playbook_executed": false' in blocked.details_json
            assert "auto_remediation.started" not in actions
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before


def test_each_target_verification_failure_does_not_retry(seeded):
    from app.presentation import job_outcome_label

    _enable(seeded)
    seeded.config["RECOVERY_CHECK"] = lambda server, action: (False, "post-check did not match the service port")
    with seeded.app_context():
        for name, instance, action, host in _TARGETS:
            sync_alerts(FakePrometheus([_alert(name, f"fp-ver-{host}", instance)]))
            alert = db.session.scalar(select(Alert).where(Alert.fingerprint == f"fp-ver-{host}"))
            jobs = db.session.scalars(
                select(AutomationJob).where(AutomationJob.alert_id == alert.id).order_by(AutomationJob.id)
            ).all()
            assert len(jobs) == 1
            assert jobs[0].action_key == action
            assert jobs[0].exit_code == 0
            assert jobs[0].verification_result == "failed"
            assert jobs[0].attempt == 1
            assert jobs[0].reason == "verification_failed"
            assert job_outcome_label(jobs[0]) == "VERIFICATION_FAILED"
            incident = db.session.get(Incident, jobs[0].incident_id)
            assert incident.verification_failed is True
            assert incident.manual_required is True
            assert incident.retry_count == 0
            assert maybe_remediate(alert) is None
            failed = db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "auto_remediation.verification_failed",
                    AuditLog.resource_id == str(jobs[0].id),
                )
            )
            executed = db.session.scalar(
                select(AuditLog).where(
                    AuditLog.action == "auto_remediation.executed",
                    AuditLog.resource_id == str(jobs[0].id),
                )
            )
            assert failed is not None
            assert executed is not None
            assert '"result": "VERIFICATION_FAILED"' in failed.details_json
            assert "verification failed after remediation" in failed.details_json
            assert "No retry was performed" in failed.details_json
            assert "Auto-remediation failed" not in failed.details_json
            assert f'"target": "{host}"' in failed.details_json
            if host == "WIN01":
                assert "post-check on port 9182 failed" in failed.details_json


def test_successful_start_and_failed_wait_does_not_retry(seeded, monkeypatch):
    from app.executors.base import ExecutionResult
    from app.models import utcnow
    from app.presentation import execution_result_label, job_outcome_label

    output = """TASK [Start app01-web container] ***
changed: [APP01]

TASK [Wait for application port 8080] ***
fatal: [APP01]: FAILED! => {"msg": "Timeout when waiting for 192.168.10.12:8080"}
"""

    def fake_run(**kwargs):
        return ExecutionResult(False, 2, output, utcnow(), utcnow())

    monkeypatch.setattr("app.executors.ansible.run_controller_playbook", fake_run)
    _enable(seeded)
    seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
    seeded.config["MANAGEMENT_CHECK"] = lambda server: None
    seeded.config["RECOVERY_CHECK"] = lambda server, action: (False, "App :8080 is down.")
    with seeded.app_context():
        sync_alerts(FakePrometheus([_alert("container_down", "fp-wait", "192.168.10.12:9100")]))
        alert = db.session.scalar(select(Alert).where(Alert.fingerprint == "fp-wait"))
        jobs = db.session.scalars(
            select(AutomationJob).where(AutomationJob.alert_id == alert.id).order_by(AutomationJob.id)
        ).all()
        assert len(jobs) == 1
        assert jobs[0].action_key == "restart_container"
        assert jobs[0].exit_code == 2
        assert jobs[0].verification_result == "failed"
        assert execution_result_label(jobs[0]) == "SUCCESS"
        assert job_outcome_label(jobs[0]) == "VERIFICATION_FAILED"
        assert jobs[0].reason == "verification_failed"
        incident = db.session.get(Incident, jobs[0].incident_id)
        assert incident.retry_count == 0
        assert incident.verification_failed is True
        assert incident.manual_required is True
        assert maybe_remediate(alert) is None


def test_each_probed_outage_uses_its_own_action(seeded):
    from app.services.remediation import consider_live_hosts

    _enable(seeded)
    seeded.config["AUTO_REMEDIATION_COOLDOWN_SECONDS"] = 0
    hosts = [
        {"name": "WEB01", "exporter": "UP", "services": [{"name": "Nginx :80", "status": "UP"}]},
        {"name": "APP01", "exporter": "UP", "services": [{"name": "App :8080", "status": "DOWN"}]},
        {"name": "WIN01", "exporter": "DOWN", "services": [{"name": "WinRM :5985", "status": "UP"}]},
    ]
    with seeded.app_context():
        alerts = consider_live_hosts(hosts)
        assert {alert.alert_name for alert in alerts} == {"container_down", "WindowsExporterDown"}
        jobs = []
        for alert in alerts:
            job = maybe_remediate(alert)
            assert job is not None
            assert job.attempt == 1
            assert job.retry_of_job_id is None
            jobs.append(job)
        assert {job.action_key for job in jobs} == {"restart_container", "restart_windows_exporter"}
        assert db.session.scalar(
            select(func.count()).select_from(AutomationJob).where(AutomationJob.action_key == "restart_nginx")
        ) == 0


def test_host_drawer_does_not_mix_another_servers_retry_limit(seeded, client):
    from app.services.audit import record

    login(client, "viewer")
    with seeded.app_context():
        app01 = db.session.scalar(select(Server).where(Server.name == "APP01"))
        record(
            "manual_intervention.required",
            "alert",
            app01.id,
            {
                "target": "WEB01",
                "action": "restart_nginx",
                "message": (
                    "Reason: retry limit. MANUAL_REQUIRED. "
                    "Auto-remediation reached the retry limit for restart_nginx."
                ),
                "result": "MANUAL_REQUIRED",
            },
            system=True,
        )
    app_text = " ".join(
        f"{item.get('title') or ''} {item.get('message') or ''}"
        for item in client.get("/dashboard/events/APP01").get_json()["events"]
    )
    web_text = " ".join(
        f"{item.get('title') or ''} {item.get('message') or ''}"
        for item in client.get("/dashboard/events/WEB01").get_json()["events"]
    )
    assert "restart_nginx" not in app_text
    assert "restart_nginx" in web_text
