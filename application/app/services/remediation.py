import re
import threading
from datetime import timedelta, timezone

from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models import Alert, AuditLog, AutomationJob, Incident, Server, utcnow
from app.services.audit import record
from app.services.automation import AutomationRejected, dispatch, enqueue_job
from app.executors.actions import action_risk
from app.services.checks import management_refusal, refuse_unreachable_management, verification_notice
from app.presentation import format_clock
from app.services.metrics import HOST_CHECKS

LAB_ACTIONS = {
    "WEB01": ("restart_nginx", {}, "Restart Nginx"),
    "APP01": ("restart_container", {"container_name": "app01-web"}, "Restart container"),
    "WIN01": ("restart_windows_exporter", {"service_name": "windows_exporter"}, "Restart Windows Exporter"),
}
_AUTO_LOCK = threading.Lock()
_AUTO_RUNNING = set()


ALERTS_FOR = {
    "WEB01": {"service_down", "InstanceDown", "NginxDown"},
    "APP01": {"container_down", "service_down"},
    "WIN01": {"service_down", "InstanceDown", "WindowsExporterDown"},
}

_DIAGNOSTIC_TOKENS = {"cpu", "memory", "ram", "disk", "latency"}
_RISKY_TOKENS = {"reboot", "cleanup", "delete", "network", "kill"}


def unreachable_message(name):
    check = HOST_CHECKS.get(name)
    if check is None:
        return None
    labels = [check["exporter_label"], *[item["name"] for item in check["services"]]]
    checks = " and ".join(labels) if len(labels) == 2 else ", ".join(labels)
    state = "are both down" if len(labels) == 2 else "are down"
    spec = LAB_ACTIONS.get(name)
    restart = f"so {spec[2]} cannot run" if spec else "so it cannot be restarted from the portal"
    return (
        f"{name} is unreachable. {checks} {state}, {restart}. "
        "Check power, network, and SSH on the machine first."
    )


def blocked_reason(server, alert=None):
    if server is None or not server.is_active or server.status != "down":
        return None
    name = (server.name or "").upper()
    if name not in LAB_ACTIONS:
        return None
    if alert is not None and (alert.status == "resolved" or alert.alert_name not in ALERTS_FOR.get(name, set())):
        return None
    return unreachable_message(name)


def suggest_remediation(server, alert=None):
    if server is None or not server.is_active:
        return None
    if alert is not None and alert.status == "resolved":
        return None
    spec = LAB_ACTIONS.get((server.name or "").upper())
    if spec is None:
        return None
    if alert is not None and alert.alert_name not in ALERTS_FOR.get(server.name.upper(), set()):
        return None
    action_key, parameters, label = spec
    return {"action_key": action_key, "parameters": dict(parameters), "label": label}


_LIVE_ALERT_NAMES = {
    "WEB01": "NginxDown",
    "APP01": "container_down",
    "WIN01": "WindowsExporterDown",
}


def consider_live_hosts(hosts):
    """A probed lab outage uses the same incident flow as a firing alert."""
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return []
    opened = []
    for host in hosts or []:
        name = (host.get("name") or "").upper()
        spec = LAB_ACTIONS.get(name)
        alert_name = _LIVE_ALERT_NAMES.get(name)
        if spec is None or alert_name is None:
            continue
        server = db.session.scalar(select(Server).where(Server.name == name))
        if server is None:
            continue
        action_key = spec[0]
        if _probe_is_down(name, host):
            opened.append(_ensure_live_alert(server, alert_name))
            continue
        if _action_is_running(server.id, action_key):
            continue
        _resolve_live_alert(server, alert_name)
        _close_restored_incident(server, action_key)
    return opened


def _probe_is_down(name, host):
    if name == "WIN01":
        return host.get("exporter") == "DOWN"
    return any(item.get("status") == "DOWN" for item in host.get("services") or [])


def _action_is_running(server_id, action_key):
    return (
        db.session.scalar(
            select(AutomationJob.id).where(
                AutomationJob.server_id == server_id,
                AutomationJob.action_key == action_key,
                AutomationJob.status.in_(("queued", "running")),
            )
        )
        is not None
    )


def _live_alert(server, alert_name):
    return db.session.scalar(
        select(Alert)
        .where(
            Alert.server_id == server.id,
            Alert.alert_name == alert_name,
            Alert.source == "live",
        )
        .order_by(Alert.id.desc())
    )


def _ensure_live_alert(server, alert_name):
    firing = db.session.scalar(
        select(Alert)
        .where(
            Alert.server_id == server.id,
            Alert.alert_name == alert_name,
            Alert.status == "firing",
        )
        .order_by(Alert.id.desc())
    )
    if firing is not None:
        return firing
    alert = _live_alert(server, alert_name)
    now = utcnow()
    if alert is None:
        alert = Alert(
            server_id=server.id,
            fingerprint=f"live:{server.name}:{alert_name}"[:128],
            alert_name=alert_name,
            category="availability",
            source="live",
            severity="critical",
            status="firing",
            summary=f"{server.name} {alert_name}",
            description=f"{server.name} service is down.",
            starts_at=now,
            created_at=now,
        )
        db.session.add(alert)
    else:
        alert.status = "firing"
        alert.resolved_at = None
        alert.starts_at = now
    db.session.commit()
    return alert


def _close_restored_incident(server, action_key):
    incident = _current_incident(server.id, action_key)
    if incident is None:
        return None
    alert = db.session.get(Alert, incident.alert_id) if incident.alert_id else None
    if alert is None:
        incident.status = "resolved"
        incident.closed_at = utcnow()
        incident.reason = "service restored"
        db.session.commit()
        return incident
    return _resolve_incident(incident, server, alert, "service restored")


def _resolve_live_alert(server, alert_name):
    alert = _live_alert(server, alert_name)
    if alert is None or alert.status == "resolved":
        return
    alert.status = "resolved"
    alert.resolved_at = utcnow()
    db.session.commit()


def schedule_auto_remediation(alerts):
    """Consider firing alerts without blocking the dashboard request on Ansible."""
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return
    app = current_app._get_current_object()
    for alert in alerts or []:
        if getattr(alert, "status", None) != "firing":
            continue
        with _AUTO_LOCK:
            if alert.id in _AUTO_RUNNING:
                continue
            _AUTO_RUNNING.add(alert.id)

        def _run(alert_id=alert.id):
            try:
                with app.app_context():
                    try:
                        current = db.session.get(Alert, alert_id)
                        if current is not None:
                            maybe_remediate(current)
                    finally:
                        db.session.remove()
            finally:
                with _AUTO_LOCK:
                    _AUTO_RUNNING.discard(alert_id)

        threading.Thread(target=_run, name=f"auto-remediate-{alert.id}", daemon=True).start()


def maybe_remediate(alert):
    """Failure, then this incident, management, policy, duplicate, cooldown, execute, verify."""
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return None
    if alert is None or alert.status != "firing" or alert.server_id is None:
        return None
    server = db.session.get(Server, alert.server_id)
    if server is None:
        return None
    if server.status == "maintenance":
        _note_once(
            "auto_remediation.skipped",
            alert,
            {
                "message": (
                    f"Reason: maintenance. {server.name} is in maintenance. "
                    "Monitoring continues. Auto-remediation was not started."
                ),
                "alert_id": alert.id,
                "server_id": server.id,
                "reason": "maintenance",
            },
        )
        return None
    suggestion = suggest_remediation(server, alert)
    if suggestion is None:
        if _is_diagnostic(alert):
            _note_once(
                "auto_remediation.skipped",
                alert,
                {
                    "message": (
                        f"Reason: diagnostic. {alert.alert_name} is a warning only. "
                        "Auto-remediation does not reboot, clean up disk, delete files, or change the network."
                    ),
                    "alert_id": alert.id,
                    "reason": "diagnostic",
                },
            )
        else:
            _note_manual(
                alert,
                None,
                "Reason: no allow-listed action. MANUAL_REQUIRED. This alert has no allow-listed remediation action.",
            )
        return None
    action_key = suggestion["action_key"]
    risk = action_risk(action_key)
    if risk != "low":
        _note_manual(
            alert,
            action_key,
            f"Reason: risk. MANUAL_REQUIRED. {action_key} is {risk} risk, so auto-remediation did not run.",
        )
        return None
    up, up_detail = _service_already_up(action_key)
    if up:
        _resolve_open_incident(server, action_key, alert, "service restored")
        _note_once(
            "auto_remediation.skipped",
            alert,
            {
                "message": (
                    f"Reason: service is up. {action_key} on {server.name} is already answering. "
                    "Auto-remediation was not started."
                ),
                "action_key": action_key,
                "alert_id": alert.id,
                "reason": "service is up",
                "target": server.name,
                "action": action_key,
                "trigger": "auto",
                "result": "SKIPPED",
            },
        )
        return None
    incident = _current_incident(server.id, action_key)
    if incident is not None and _incident_is_terminal(incident):
        _note_terminal(alert, action_key, incident)
        return None
    refusal = management_refusal(server, action_key)
    if refusal:
        if incident is None:
            incident = _create_incident(server, alert, action_key)
        _mark_blocked(incident, server, alert, action_key, refusal)
        return None
    if incident is not None:
        _clear_channel_block(incident)
    if incident is None and _in_cooldown(server.id, action_key):
        _note_management(alert, server, action_key, None, "PASS", "management channel is up")
        _note_cooldown(alert, server, action_key)
        return None
    active = _active_conflict(server.id, action_key, alert.id)
    if active and incident is None:
        _note_management(alert, server, action_key, None, "PASS", "management channel is up")
        _note_duplicate(alert, action_key, active)
        return None
    if incident is None:
        incident = _create_incident(server, alert, action_key)
    _note_management(alert, server, action_key, incident.id, "PASS", "management channel is up")
    if active:
        _note_duplicate(alert, action_key, active)
        return None
    if not _incident_has_execution(incident) and _in_cooldown(server.id, action_key):
        _note_cooldown(alert, server, action_key)
        return None
    try:
        return _continue_incident(server, alert, suggestion, incident)
    except AutomationRejected:
        current_app.logger.info("Auto-remediation skipped")
        return None


def alert_auto_notice(alert):
    entry = db.session.scalar(
        select(AuditLog)
        .where(
            AuditLog.resource_type == "alert",
            AuditLog.resource_id == str(alert.id),
            AuditLog.action.in_(("auto_remediation.skipped", "manual_intervention.required", "auto_remediation.blocked")),
        )
        .order_by(AuditLog.id.desc())
    )
    if entry is None:
        return None
    newer = db.session.scalar(
        select(AuditLog.id).where(
            AuditLog.resource_type == "alert",
            AuditLog.resource_id == str(alert.id),
            AuditLog.id > entry.id,
            AuditLog.action.in_(
                (
                    "auto_remediation.requested",
                    "auto_remediation.verified",
                    "incident.created",
                    "incident.resolved",
                )
            ),
        )
    )
    if newer is not None:
        return None
    return _message(entry)


def job_auto_context(job):
    cooldown = None
    if job.alert_id is not None and job.created_at is not None:
        entry = db.session.scalar(
            select(AuditLog)
            .where(
                AuditLog.resource_type == "alert",
                AuditLog.resource_id == str(job.alert_id),
                AuditLog.action == "auto_remediation.skipped",
            )
            .order_by(AuditLog.id.desc())
        )
        if (
            entry is not None
            and "cooldown" in (entry.details_json or "")
            and _aware(entry.created_at) >= _aware(job.created_at)
        ):
            cooldown = _message(entry)
    incident = db.session.get(Incident, job.incident_id) if getattr(job, "incident_id", None) else None
    retry_count = incident.retry_count if incident is not None else job_retry_depth(job)
    final = getattr(job, "final_status", None)
    intervention = None
    if final == "BLOCKED" or job.verification_result == "blocked":
        intervention = f"BLOCKED. {job.block_reason or job.verification_detail or 'The playbook was not started.'}".strip()
    elif final == "VERIFICATION_FAILED" or job.verification_result == "failed":
        _reason, notice = verification_notice(job.action_key)
        intervention = notice
    elif final == "MANUAL_REQUIRED" or (
        job.trigger_source == "auto" and job.status == "failed" and _execution_retries_used(job)
    ):
        intervention = f"MANUAL_REQUIRED. Auto-remediation reached the retry limit for {job.action_key}."
    return {
        "retry_count": retry_count,
        "cooldown": cooldown,
        "intervention": intervention,
    }


def job_retry_depth(job):
    depth = 0
    current = job
    seen = set()
    while current is not None and current.retry_of_job_id and current.id not in seen:
        seen.add(current.id)
        depth += 1
        current = db.session.get(AutomationJob, current.retry_of_job_id)
        if depth > 10:
            break
    return depth


def _trace(server, action_key, result, reason, **extra):
    payload = {
        "target": getattr(server, "name", None),
        "action": action_key,
        "action_key": action_key,
        "trigger": "auto",
        "result": result,
        "reason": reason,
        "server_id": getattr(server, "id", None),
    }
    payload.update(extra)
    return payload


def _current_incident(server_id, action_key):
    return db.session.scalar(
        select(Incident)
        .where(
            Incident.server_id == server_id,
            Incident.action_key == action_key,
            Incident.status == "open",
        )
        .order_by(Incident.id.desc())
    )


def _incident_is_terminal(incident):
    if incident.verification_failed or incident.reason == "verification_failed":
        return True
    return bool(incident.manual_required and incident.reason == "retry_limit")


def _note_terminal(alert, action_key, incident):
    if incident.reason == "verification_failed" or incident.verification_failed:
        _reason, notice = verification_notice(action_key)
        _note_manual(alert, action_key, notice, reason="manual intervention required")
        return
    _note_manual(
        alert,
        action_key,
        f"Reason: retry limit. MANUAL_REQUIRED. Auto-remediation reached the retry limit for {action_key}.",
    )


def _create_incident(server, alert, action_key):
    incident = Incident(
        server_id=server.id,
        alert_id=alert.id,
        action_key=action_key,
        status="open",
        retry_count=0,
        manual_required=False,
        verification_failed=False,
        blocked=False,
        opened_at=utcnow(),
    )
    db.session.add(incident)
    db.session.commit()
    record(
        "incident.created",
        "alert",
        alert.id,
        {
            "message": f"Incident {incident.id} opened for {action_key} on {server.name}.",
            "reason": "incident created",
            "result": "OPEN",
            "target": server.name,
            "action": action_key,
            "trigger": "auto",
            "incident_id": incident.id,
            "retry_count": 0,
            "manual_required": False,
            "verification_failed": False,
            "blocked": False,
            "alert_id": alert.id,
        },
        system=True,
    )
    return incident


def _resolve_incident(incident, server, alert, reason):
    if incident is None or incident.status == "resolved":
        return None
    incident.status = "resolved"
    incident.closed_at = utcnow()
    incident.reason = reason
    db.session.commit()
    record(
        "incident.resolved",
        "alert",
        alert.id,
        {
            "message": (
                f"Incident {incident.id} resolved ({reason}). "
                "The next failure starts a new incident at retry_count 0."
            ),
            "reason": reason,
            "result": "RESOLVED",
            "target": server.name,
            "action": incident.action_key,
            "trigger": "auto",
            "incident_id": incident.id,
            "alert_id": alert.id,
        },
        system=True,
    )
    return incident


def _resolve_open_incident(server, action_key, alert, reason):
    return _resolve_incident(_current_incident(server.id, action_key), server, alert, reason)


def _note_management(alert, server, action_key, incident_id, result, reason):
    _note_once(
        "management.check",
        alert,
        {
            "message": f"Management check {result} for {action_key} on {server.name}.",
            "reason": reason,
            "result": result,
            "target": server.name,
            "action": action_key,
            "trigger": "auto",
            "incident_id": incident_id,
            "alert_id": alert.id,
            "playbook_executed": False,
        },
    )


def _mark_blocked(incident, server, alert, action_key, refusal):
    first = not incident.blocked
    incident.blocked = True
    incident.manual_required = True
    incident.verification_failed = False
    incident.reason = "management_channel_unavailable"
    db.session.commit()
    text = refusal.get("message") or "Management channel is down."
    message = (
        "Reason: management_channel_unavailable. BLOCKED. "
        f"{text} The playbook was not started."
    )
    if first:
        refuse_unreachable_management(server, action_key=action_key, alert_id=alert.id)
    payload = {
        "message": message,
        "reason": "management_channel_unavailable",
        "result": "BLOCKED",
        "target": server.name,
        "action": action_key,
        "action_key": action_key,
        "trigger": "auto",
        "playbook_executed": False,
        "incident_id": incident.id,
        "alert_id": alert.id,
    }
    _note_once("management.check", alert, payload)
    _note_once("auto_remediation.blocked", alert, payload)
    _note_manual(alert, action_key, message)


def _clear_channel_block(incident):
    if incident.reason != "management_channel_unavailable":
        return
    incident.blocked = False
    incident.manual_required = False
    incident.reason = None
    db.session.commit()


def _note_cooldown(alert, server, action_key):
    seconds = int(current_app.config.get("AUTO_REMEDIATION_COOLDOWN_SECONDS", 120))
    latest = _last_success_job(server.id, action_key)
    moment = _aware((latest.finished_at or latest.created_at) if latest is not None else None) or utcnow()
    ready = format_clock(moment + timedelta(seconds=seconds))
    ran = format_clock(moment)
    job_bit = f" as job {latest.id}" if latest is not None else ""
    _note_once(
        "auto_remediation.skipped",
        alert,
        {
            "message": (
                f"Reason: Cooldown. {action_key} on {server.name} last ran at {ran}{job_bit}. "
                f"Auto-remediation was skipped. The next auto run can start at {ready}."
            ),
            "action_key": action_key,
            "action": action_key,
            "target": server.name,
            "trigger": "auto",
            "alert_id": alert.id,
            "reason": "cooldown",
            "result": "COOLDOWN_SKIPPED",
            "cooldown_seconds": seconds,
            "last_job_id": None if latest is None else latest.id,
            "next_run_at": ready,
        },
    )


def _note_duplicate(alert, action_key, message):
    server = db.session.get(Server, alert.server_id) if alert.server_id else None
    _note_once(
        "auto_remediation.skipped",
        alert,
        {
            "message": message,
            "action_key": action_key,
            "action": action_key,
            "target": None if server is None else server.name,
            "trigger": "auto",
            "alert_id": alert.id,
            "reason": "duplicate",
            "result": "DUPLICATE_SKIPPED",
        },
    )


def _latest_incident_job(incident):
    return db.session.scalars(
        select(AutomationJob).where(AutomationJob.incident_id == incident.id).order_by(AutomationJob.id.desc())
    ).first()


def _incident_has_execution(incident):
    for row in db.session.scalars(select(AutomationJob).where(AutomationJob.incident_id == incident.id)).all():
        if row.final_status == "BLOCKED" or row.verification_result == "blocked":
            continue
        return True
    return False


def _continue_incident(server, alert, suggestion, incident):
    last = _latest_incident_job(incident)
    if last is not None and (last.final_status == "BLOCKED" or last.verification_result == "blocked"):
        last = None
    if last is not None and last.status in ("queued", "running"):
        return None
    if last is None:
        return _start_auto(server, alert, suggestion, incident, retry_of=None)
    if _execution_failed(last) and incident.retry_count < _max_retries():
        if not incident.retry_count:
            incident.retry_count = 1
            db.session.commit()
        return _start_auto(server, alert, suggestion, incident, retry_of=last.id)
    if _execution_failed(last):
        incident.manual_required = True
        incident.verification_failed = False
        incident.blocked = False
        incident.reason = "retry_limit"
        db.session.commit()
        _note_manual(
            alert,
            suggestion["action_key"],
            (
                "Reason: retry limit. MANUAL_REQUIRED. "
                f"Auto-remediation reached the retry limit for {suggestion['action_key']}."
            ),
        )
        return None
    return None


def _stamp(job, final_status, reason):
    job.final_status = final_status
    job.reason = reason
    db.session.commit()


def _start_auto(server, alert, suggestion, incident, retry_of=None):
    action_key = suggestion["action_key"]
    attempt = (incident.retry_count or 0) + 1
    details = _trace(
        server,
        action_key,
        "RUNNING",
        f"Auto-remediation requested {action_key}.",
        alert_id=alert.id,
        incident_id=incident.id,
        attempt=attempt,
    )
    if retry_of is not None:
        record(
            "auto_remediation.retry",
            "alert",
            alert.id,
            {
                **details,
                "message": f"Auto-remediation retry for {action_key}.",
                "reason": "retry",
                "result": "RETRY",
                "retry_of_job_id": retry_of,
                "retry_count": incident.retry_count,
            },
            system=True,
        )
    record(
        "auto_remediation.requested",
        "alert",
        alert.id,
        {**details, "message": f"Auto-remediation requested {action_key}.", "trigger": "auto"},
        system=True,
    )
    record(
        "remediation.request",
        "alert",
        alert.id,
        {"action_key": action_key, "alert_id": alert.id, "incident_id": incident.id, "attempt": attempt},
        system=True,
    )
    job = enqueue_job(
        server_id=server.id,
        action_key=action_key,
        parameters=dict(suggestion["parameters"]),
        trigger_source="auto",
        requested_by=None,
        alert_id=alert.id,
        retry_of_job_id=retry_of,
        incident_id=incident.id,
        attempt=attempt,
    )
    record(
        "auto_remediation.started",
        "automation_job",
        job.id,
        {
            **details,
            "message": f"Auto-remediation started {action_key}.",
            "trigger": "auto",
            "result": "RUNNING",
            "reason": "remediation started",
            "playbook_executed": True,
        },
        system=True,
    )
    job = dispatch(job.id, actor=None)
    return _finish_auto(job, server, alert, suggestion, incident)


def _finish_auto(job, server, alert, suggestion, incident):
    action_key = suggestion["action_key"]
    details = _trace(
        server,
        action_key,
        "FAILED",
        job.verification_detail or "Auto-remediation failed.",
        alert_id=alert.id,
        exit_code=job.exit_code,
        verification_result=job.verification_result,
        incident_id=None if incident is None else incident.id,
        attempt=job.attempt,
    )
    if job.status == "succeeded":
        message = job.verification_detail or "Auto-remediation verified."
        _stamp(job, "SUCCESS", "success")
        record(
            "auto_remediation.verified",
            "automation_job",
            job.id,
            {**details, "result": "SUCCESS", "message": message, "reason": message},
            system=True,
        )
        if incident is not None:
            _resolve_incident(incident, server, alert, "success")
        return job
    if job.verification_result == "blocked":
        reason = job.block_reason or job.verification_detail or "Management channel is down."
        message = (
            "Reason: management_channel_unavailable. BLOCKED. "
            f"{reason} The playbook was not started."
        )
        _stamp(job, "BLOCKED", "management_channel_unavailable")
        if incident is not None:
            incident.blocked = True
            incident.manual_required = True
            incident.reason = "management_channel_unavailable"
            db.session.commit()
        record(
            "auto_remediation.blocked",
            "automation_job",
            job.id,
            {
                **details,
                "result": "BLOCKED",
                "message": message,
                "reason": "management_channel_unavailable",
                "playbook_executed": False,
            },
            system=True,
        )
        _note_manual(alert, action_key, message)
        return job
    if job.verification_result == "failed":
        reason, message = verification_notice(action_key)
        job.verification_detail = reason
        _stamp(job, "VERIFICATION_FAILED", "verification_failed")
        if incident is not None:
            incident.verification_failed = True
            incident.manual_required = True
            incident.blocked = False
            incident.reason = "verification_failed"
            db.session.commit()
        record(
            "auto_remediation.executed",
            "automation_job",
            job.id,
            {
                **details,
                "result": "SUCCESS",
                "message": "Remediation execution succeeded. The remediation command completed successfully.",
                "reason": "remediation execution succeeded",
                "execution_result": "SUCCESS",
            },
            system=True,
        )
        record(
            "auto_remediation.verification_failed",
            "automation_job",
            job.id,
            {
                **details,
                "result": "VERIFICATION_FAILED",
                "message": message,
                "reason": "verification failed after remediation",
                "execution_result": "SUCCESS",
            },
            system=True,
        )
        _note_manual(alert, action_key, message, reason="manual intervention required")
        return job
    message = job.verification_detail or "The command failed before verification."
    if incident is not None and incident.retry_count < _max_retries():
        incident.retry_count += 1
        db.session.commit()
        _stamp(job, "EXECUTION_FAILED", "execution_failed")
        record(
            "auto_remediation.failed",
            "automation_job",
            job.id,
            {
                **details,
                "result": "EXECUTION_FAILED",
                "message": f"Reason: execution failed. {message}",
                "reason": "execution_failed",
                "retry_count": incident.retry_count,
            },
            system=True,
        )
        return _start_auto(server, alert, suggestion, incident, retry_of=job.id)
    _stamp(job, "MANUAL_REQUIRED", "retry_limit")
    if incident is not None:
        incident.manual_required = True
        incident.verification_failed = False
        incident.blocked = False
        incident.reason = "retry_limit"
        db.session.commit()
    record(
        "auto_remediation.failed",
        "automation_job",
        job.id,
        {
            **details,
            "result": "MANUAL_REQUIRED",
            "message": f"Reason: execution failed. {message}",
            "reason": "retry_limit",
        },
        system=True,
    )
    _note_manual(
        alert,
        action_key,
        f"Reason: retry limit. MANUAL_REQUIRED. Auto-remediation reached the retry limit for {action_key}.",
    )
    return job


def _is_diagnostic(alert):
    tokens = set(re.split(r"[^a-z0-9]+", (alert.alert_name or "").lower()))
    return bool(tokens & (_DIAGNOSTIC_TOKENS | _RISKY_TOKENS))


def _verification_failed(job):
    return job is not None and job.verification_result == "failed"


def _execution_failed(job):
    return job is not None and job.status == "failed" and job.verification_result == "skipped"


def _retry_due(alert, action_key, job):
    return _execution_failed(job) and _auto_retry_count(alert, action_key) < _max_retries()


def _retry_exhausted(alert, action_key, last):
    if not _execution_failed(last):
        return False
    return _auto_retry_count(alert, action_key) >= _max_retries()


def _execution_retries_used(job):
    if job.alert_id is None:
        return job_retry_depth(job) >= _max_retries()
    alert = db.session.get(Alert, job.alert_id)
    if alert is None:
        return job_retry_depth(job) >= _max_retries()
    return _auto_retry_count(alert, job.action_key) >= _max_retries()


def _service_already_up(action_key):
    """A stuck firing alert must not restart a service that is already answering."""
    if current_app.config.get("AUTOMATION_EXECUTOR") != "ansible":
        return False, ""
    checker = current_app.config.get("RECOVERY_CHECK")
    if checker is not None:
        ok, detail = checker(None, action_key)
        return bool(ok), detail or ""
    from app.services.checks import SERVICE_CHECKS
    from app.services.probes import http_probe, tcp_probe

    spec = SERVICE_CHECKS.get(action_key)
    if spec is None:
        return False, ""
    kind, target, label = spec
    if kind == "http":
        ok, latency = http_probe(target, timeout=2)
    else:
        host, port = target
        ok, latency = tcp_probe(host, port, timeout=2)
    if not ok:
        return False, ""
    return True, f"{label} is up ({latency} ms)."


def _auto_jobs_for_incident(alert, action_key):
    """Jobs since the latest success. A blocked attempt does not use the retry budget."""
    rows = db.session.scalars(
        select(AutomationJob)
        .where(
            AutomationJob.alert_id == alert.id,
            AutomationJob.action_key == action_key,
            AutomationJob.trigger_source.in_(("auto", "remediation")),
        )
        .order_by(AutomationJob.id.desc())
    ).all()
    started = _aware(alert.starts_at)
    current = []
    for row in rows:
        created = _aware(row.created_at)
        if started is not None and (created is None or created < started):
            continue
        if row.status == "succeeded" or row.verification_result == "passed":
            break
        if row.verification_result == "blocked":
            continue
        current.append(row)
    return current


def _auto_retry_count(alert, action_key):
    return sum(1 for row in _auto_jobs_for_incident(alert, action_key) if row.retry_of_job_id is not None)


def _latest_auto_job(alert, action_key):
    rows = _auto_jobs_for_incident(alert, action_key)
    return rows[0] if rows else None


def _active_conflict(server_id, action_key, alert_id):
    active = ("queued", "running")
    same_action = db.session.scalar(
        select(AutomationJob.id).where(
            AutomationJob.server_id == server_id,
            AutomationJob.action_key == action_key,
            AutomationJob.status.in_(active),
        )
    )
    if same_action is not None:
        return (
            f"Reason: duplicate. Job {same_action} for this server and action is already queued or running, "
            "so auto-remediation did not create another job."
        )
    same_alert = db.session.scalar(
        select(AutomationJob.id).where(
            AutomationJob.alert_id == alert_id,
            AutomationJob.trigger_source.in_(("auto", "remediation")),
            AutomationJob.status.in_(active),
        )
    )
    if same_alert is not None:
        return (
            f"Reason: duplicate. Auto job {same_alert} for this alert is already queued or running, "
            "so auto-remediation did not create another job."
        )
    return None


def _last_success_job(server_id, action_key):
    return db.session.scalars(
        select(AutomationJob)
        .where(
            AutomationJob.server_id == server_id,
            AutomationJob.action_key == action_key,
            AutomationJob.trigger_source.in_(("auto", "remediation")),
            AutomationJob.status == "succeeded",
        )
        .order_by(AutomationJob.id.desc())
    ).first()


def _in_cooldown(server_id, action_key):
    seconds = int(current_app.config.get("AUTO_REMEDIATION_COOLDOWN_SECONDS", 120))
    if seconds <= 0:
        return False
    latest = _last_success_job(server_id, action_key)
    if latest is None:
        return False
    moment = latest.finished_at or latest.created_at
    moment = _aware(moment)
    if moment is None:
        return False
    return utcnow() - moment < timedelta(seconds=seconds)


def _max_retries():
    return max(0, int(current_app.config.get("AUTO_REMEDIATION_MAX_RETRIES", 1)))


def _note_manual(alert, action_key, message, reason=None):
    server = db.session.get(Server, alert.server_id) if alert.server_id else None
    _note_once(
        "manual_intervention.required",
        alert,
        {
            "message": message,
            "reason": reason or message,
            "action": action_key,
            "action_key": action_key,
            "alert_id": alert.id,
            "target": None if server is None else server.name,
            "trigger": "auto",
            "result": "MANUAL_REQUIRED",
        },
    )


def _note_once(action, alert, details):
    previous = db.session.scalar(
        select(AuditLog)
        .where(
            AuditLog.action == action,
            AuditLog.resource_type == "alert",
            AuditLog.resource_id == str(alert.id),
        )
        .order_by(AuditLog.id.desc())
    )
    if previous is not None and _message(previous) == details.get("message"):
        return previous
    return record(action, "alert", alert.id, details, system=True)


def _aware(value):
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _message(entry):
    import json

    try:
        data = json.loads(entry.details_json or "{}")
    except json.JSONDecodeError:
        return entry.details_json or ""
    if isinstance(data, dict):
        return data.get("message") or ""
    return ""
