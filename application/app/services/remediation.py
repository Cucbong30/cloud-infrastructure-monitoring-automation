import re
import threading
from datetime import timedelta, timezone

from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models import Alert, AuditLog, AutomationJob, Incident, Server, utcnow
from app.services.audit import record
from app.services.automation import AutomationRejected, RemediationUnavailable, dispatch, enqueue_job
from app.executors.actions import SERVICE_LABELS, action_risk
from app.services.runbooks import (
    classify_incident,
    incident_signal,
    observed_docker_active,
    probe_incident_type,
)
from app.services.checks import management_refusal, refuse_unreachable_management, verification_notice
from app.presentation import format_clock
from app.services.metrics import HOST_CHECKS

TARGET_ACTIONS = {
    "WEB01": [("restart_nginx", {}, "Restart Nginx")],
    "APP01": [
        ("restart_container", {"container_name": "app01-web"}, "Restart container"),
        ("restart_docker_service", {}, "Restart Docker"),
    ],
    "WIN01": [("restart_windows_exporter", {"service_name": "windows_exporter"}, "Restart Windows Exporter")],
    "AZURE01": [
        ("restart_nginx", {}, "Restart Nginx"),
        ("reboot_server", {}, "Reboot server"),
    ],
}
LAB_ACTIONS = {name: items[0] for name, items in TARGET_ACTIONS.items()}


def actions_for(server_name):
    return list(TARGET_ACTIONS.get((server_name or "").upper(), []))
_AUTO_LOCK = threading.Lock()
_AUTO_RUNNING = set()


ALERTS_FOR = {
    "WEB01": {"service_down", "InstanceDown", "NginxDown"},
    "APP01": {"container_down", "service_down"},
    "WIN01": {"service_down", "InstanceDown", "WindowsExporterDown"},
    "AZURE01": {"service_down", "InstanceDown", "NginxDown", "AzureNginxDown", "nginx_down"},
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


def docker_service_active(server, alert=None):
    """False when this host already reports the Docker service down. Otherwise the caller may pass a check."""
    checker = current_app.config.get("DOCKER_ACTIVE_CHECK")
    if alert is not None and incident_signal(alert.alert_name) == "docker_service_down":
        return False
    if checker is not None:
        return bool(checker(server))
    if server is None:
        return True
    rows = db.session.scalars(
        select(Alert).where(Alert.server_id == server.id, Alert.status == "firing")
    ).all()
    return not any(incident_signal(row.alert_name) == "docker_service_down" for row in rows)


def resolve_plan(server, alert=None, requested_action=None):
    """Shared pre-check for auto, manual, and retry."""
    refusal = None if server is None else management_refusal(server, requested_action)
    plan = classify_incident(
        None if server is None else server.name,
        None if alert is None else alert.alert_name,
        management_down=False,
        docker_active=docker_service_active(server, alert),
        requested_action=requested_action,
    )
    plan["refusal"] = refusal
    plan["blocked"] = refusal is not None and bool(plan.get("action_key"))
    plan["parameters"] = {}
    plan["label"] = plan["incident_type"]
    spec = _action_spec(None if server is None else server.name, plan.get("action_key"))
    if spec is not None:
        plan["parameters"] = dict(spec[1])
        plan["label"] = spec[2]
    return plan


def _action_spec(server_name, action_key):
    if not action_key:
        return None
    return next((item for item in TARGET_ACTIONS.get((server_name or "").upper(), []) if item[0] == action_key), None)


def suggest_remediation(server, alert=None):
    """Return the mapped action after the cause pre-check. Unknown and blocked causes return None."""
    if server is None or not server.is_active:
        return None
    if alert is not None and alert.status == "resolved":
        return None
    requested = None
    if alert is None:
        requested = (LAB_ACTIONS.get((server.name or "").upper()) or [None])[0]
    plan = resolve_plan(server, alert, requested_action=requested)
    if plan["blocked"]:
        action_key = requested or (LAB_ACTIONS.get((server.name or "").upper()) or [None])[0]
        spec = _action_spec(server.name, action_key)
        if spec is None:
            return None
        return {
            "action_key": spec[0],
            "parameters": dict(spec[1]),
            "label": spec[2],
            "incident_type": "management_unavailable",
        }
    if plan["investigate"] or not plan.get("action_key"):
        return None
    return {
        "action_key": plan["action_key"],
        "parameters": plan["parameters"],
        "label": plan["label"],
        "incident_type": plan["incident_type"],
    }


def consider_live_hosts(hosts):
    """Name the cause from the probe, then let the runbook choose the action. No default LOW action."""
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return []
    opened = []
    for host in hosts or []:
        name = (host.get("name") or "").upper()
        if name == "AZURE01":
            from app.services.inventory import azure_settings

            if not azure_settings()["configured"]:
                continue
        if not any(row["host"] == name for row in _runbook_rows()):
            continue
        server = db.session.scalar(select(Server).where(Server.name == name))
        if server is None:
            continue
        incident_type = probe_incident_type(host)
        if incident_type is None:
            _settle_live_host(server)
            continue
        observed = observed_docker_active(host)
        if incident_type == "container_down" and observed is None:
            docker_active = False
        else:
            docker_active = True if observed is None else observed
        plan = classify_incident(name, incident_type, docker_active=docker_active)
        if not plan.get("action_key"):
            continue
        _retire_other_live_alerts(server, plan["incident_type"])
        opened.append(_ensure_live_alert(server, plan["incident_type"]))
    return opened


def _runbook_rows():
    from app.services.runbooks import RUNBOOK_MAP

    return RUNBOOK_MAP


DUPLICATE_REASON = "An active remediation job already exists for this target and action."


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


def _auto_actor():
    class _Actor:
        id = None
        email = ""
        username = "SYSTEM"
        role = "SYSTEM"

    return _Actor()


def _deny_request(server, action_key, actor):
    role = (getattr(actor, "role", None) or "unknown").capitalize()
    record(
        "permission.denied",
        "approval_request",
        None,
        {
            "message": f"Permission denied for {role} role",
            "result": "DENIED",
            "risk": action_risk(action_key).upper(),
            "action": action_key,
            "action_key": action_key,
            "target": None if server is None else server.name,
            "mode": "MANUAL",
            "trigger": "manual",
            "playbook_executed": False,
            "execution_result": "NOT_RUN",
            "verification_result": "NOT_RUN",
        },
        user_id=getattr(actor, "id", None),
    )


def trigger_manual_remediation(
    server, action_key, parameters, actor, alert_id=None, approval_request=None, bound_incident=None
):
    """One operator click. MEDIUM and HIGH stop until a permitted approver accepts."""
    from app.models import User

    if server is None or not getattr(server, "is_active", False):
        raise AutomationRejected("Server is not available.")
    actor_row = db.session.get(User, getattr(actor, "id", None)) if getattr(actor, "id", None) else None
    from app.services.approval import ApprovalForbidden, can_request

    alert = db.session.get(Alert, alert_id) if alert_id else None
    plan = resolve_plan(server, alert, requested_action=action_key)
    if plan["blocked"]:
        raise RemediationUnavailable((plan["refusal"] or {}).get("message") or "Management channel is down.")
    if plan["investigate"] or not plan.get("action_key"):
        raise RemediationUnavailable("Cause was not identified. No remediation action was started.")
    if plan["action_key"] != action_key:
        action_key = plan["action_key"]
        parameters = plan["parameters"]
    if not can_request(actor_row or actor, action_key):
        _deny_request(server, action_key, actor_row or actor)
        raise ApprovalForbidden(f"Permission denied for {(getattr(actor_row or actor, 'role', None) or 'unknown').capitalize()} role")
    _bind_incident(bound_incident, server, action_key)
    if approval_request is None and action_risk(action_key) != "low":
        from app.services.approval import ApprovalPending, open_request

        raise ApprovalPending(open_request(server, action_key, parameters, actor_row or actor, alert_id))
    email = ((actor_row.email if actor_row is not None else None) or "").strip()
    triggered_by = email or (actor_row.username if actor_row is not None else "") or "unknown"
    role = None if actor_row is None else actor_row.role
    if _action_is_running(server.id, action_key):
        return _skip_duplicate(server, action_key, actor_row, triggered_by, role)
    incident = _open_manual_incident(server, action_key, alert_id)
    job = enqueue_job(
        server_id=server.id,
        action_key=action_key,
        parameters=parameters,
        trigger_source="manual",
        requested_by=None if actor_row is None else actor_row.id,
        alert_id=alert_id,
        incident_id=incident.id,
        attempt=1,
    )
    from app.services.incidents import enter_progress

    enter_progress(incident, f"{action_key} started.", actor=actor_row, job_id=job.id)
    db.session.commit()
    job = dispatch(job.id, actor=actor_row)
    _apply_manual_incident(incident, job)
    return job


def _bind_incident(incident, server, action_key):
    """Keep the job and approval on the incident the operator already opened."""
    if incident is None or server is None or getattr(incident, "server_id", None) != server.id:
        return
    if incident.status not in {"open", "acknowledged"}:
        return
    other = _current_incident(server.id, action_key)
    if other is not None and other.id != incident.id:
        return
    incident.action_key = action_key
    db.session.commit()


def _skip_duplicate(server, action_key, actor_row, triggered_by, role):
    now = utcnow()
    job = AutomationJob(
        server_id=server.id,
        requested_by=None if actor_row is None else actor_row.id,
        trigger_source="manual",
        executor=current_app.config.get("AUTOMATION_EXECUTOR", "mock"),
        action_key=action_key,
        parameters_json="{}",
        status="canceled",
        final_status="DUPLICATE_SKIPPED",
        reason=DUPLICATE_REASON,
        mode="MANUAL",
        triggered_by=triggered_by,
        user_email=triggered_by if "@" in triggered_by else None,
        user_role=role,
        created_at=now,
        started_at=now,
        finished_at=now,
    )
    db.session.add(job)
    db.session.commit()
    record(
        "remediation.skipped",
        "automation_job",
        job.id,
        {
            "target": server.name,
            "service": SERVICE_LABELS.get(action_key, action_key),
            "action": action_key,
            "action_key": action_key,
            "trigger": "manual",
            "mode": "MANUAL",
            "triggered_by": triggered_by,
            "user_email": job.user_email,
            "user_role": role,
            "actor": triggered_by,
            "role": role,
            "result": "DUPLICATE_SKIPPED",
            "final_status": "DUPLICATE_SKIPPED",
            "execution_result": "NOT_RUN",
            "verification_result": "NOT_RUN",
            "reason": DUPLICATE_REASON,
            "message": DUPLICATE_REASON,
            "job_id": job.id,
            "playbook_executed": False,
        },
        user_id=None if actor_row is None else actor_row.id,
    )
    return job


def _open_manual_incident(server, action_key, alert_id):
    current = _current_incident(server.id, action_key)
    if current is not None:
        return current
    alert = db.session.get(Alert, alert_id) if alert_id else None
    incident = Incident(
        server_id=server.id,
        alert_id=alert_id,
        action_key=action_key,
        status="open",
        severity=None if alert is None else alert.severity,
        remediation_type="manual",
        retry_count=0,
        manual_required=False,
        verification_failed=False,
        blocked=False,
        opened_at=utcnow(),
    )
    db.session.add(incident)
    db.session.commit()
    from app.services.incidents import add_event

    add_event(incident, "detected", "Service unavailable")
    db.session.commit()
    return incident


def _apply_manual_incident(incident, job):
    if incident is None or job is None:
        return
    from app.services.incidents import add_event, release_work

    final = job.final_status
    if final == "SUCCESS":
        add_event(incident, "resolved", "Recovery confirmed", to_status="resolved", job_id=job.id)
        incident.reason = "success"
    elif final == "VERIFICATION_FAILED":
        incident.verification_failed = True
        incident.manual_required = True
        incident.blocked = False
        incident.reason = "verification_failed"
        release_work(incident, "verification_failed", "Post-check failed.", job_id=job.id)
    elif final == "EXECUTION_FAILED":
        incident.manual_required = True
        incident.verification_failed = False
        incident.blocked = False
        incident.reason = "execution_failed"
        release_work(incident, "execution_failed", "Remediation command failed.", job_id=job.id)
    elif final == "MANAGEMENT_BLOCKED":
        incident.blocked = True
        incident.manual_required = True
        incident.verification_failed = False
        incident.reason = "management_channel_unavailable"
        release_work(incident, "blocked", "SSH or WinRM was down.", job_id=job.id)
    db.session.commit()


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
        from app.services.incidents import add_event

        add_event(incident, "resolved", "Service restored", to_status="resolved")
        incident.reason = "service restored"
        db.session.commit()
        return incident
    return _resolve_incident(incident, server, alert, "service restored")


def _settle_live_host(server):
    """The probe is healthy. Close only a live alert whose action is not still running."""
    rows = db.session.scalars(
        select(Alert).where(
            Alert.server_id == server.id,
            Alert.source == "live",
            Alert.status == "firing",
        )
    ).all()
    for alert in rows:
        plan = classify_incident(server.name, alert.alert_name)
        action_key = plan.get("action_key")
        if action_key and _action_is_running(server.id, action_key):
            continue
        alert.status = "resolved"
        alert.resolved_at = utcnow()
        if action_key:
            _close_restored_incident(server, action_key)
    if rows:
        db.session.commit()


def _retire_other_live_alerts(server, cause):
    """Drop a stale live cause so the scheduler cannot run the previous LOW action."""
    rows = db.session.scalars(
        select(Alert).where(
            Alert.server_id == server.id,
            Alert.source == "live",
            Alert.status == "firing",
        )
    ).all()
    changed = False
    for alert in rows:
        current = incident_signal(alert.alert_name) or alert.alert_name
        if current == cause:
            continue
        alert.status = "resolved"
        alert.resolved_at = utcnow()
        changed = True
    if changed:
        db.session.commit()


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
    plan = resolve_plan(server, alert)
    if plan["investigate"] or not plan.get("action_key"):
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
        elif (server.name or "").upper() in TARGET_ACTIONS:
            _open_investigation(server, alert)
        else:
            _note_manual(
                alert,
                None,
                "Reason: no allow-listed action. MANUAL_REQUIRED. This alert has no allow-listed remediation action.",
            )
        return None
    suggestion = {
        "action_key": plan["action_key"],
        "parameters": plan["parameters"],
        "label": plan["label"],
        "incident_type": plan["incident_type"],
    }
    action_key = suggestion["action_key"]
    up, _up_detail = _service_already_up(server, action_key)
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
    if plan["blocked"]:
        incident = _current_incident(server.id, action_key)
        if incident is None:
            incident = _create_incident(server, alert, action_key)
        _mark_blocked(incident, server, alert, action_key, plan["refusal"] or {})
        return None
    risk = action_risk(action_key)
    if risk == "high":
        if _current_incident(server.id, action_key) is None:
            _create_incident(server, alert, action_key)
        _note_manual(
            alert,
            action_key,
            (
                f"Reason: risk. MANUAL_REQUIRED. {action_key} is HIGH. "
                "An admin must request and approve it. Auto-remediation did not run."
            ),
        )
        return None
    if risk != "low":
        from app.services.approval import open_request

        open_request(server, action_key, suggestion["parameters"], _auto_actor(), alert.id)
        _note_manual(
            alert,
            action_key,
            f"Reason: risk. MANUAL_REQUIRED. {action_key} is {risk} risk, so auto-remediation did not run.",
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
        "environment": getattr(server, "environment", None),
        "provider": getattr(server, "provider", None),
        "action": action_key,
        "action_key": action_key,
        "service": SERVICE_LABELS.get(action_key, action_key),
        "trigger": "auto",
        "mode": "AUTO",
        "triggered_by": "SYSTEM",
        "user_role": "SYSTEM",
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
            Incident.status.in_(("open", "acknowledged", "in_progress")),
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
        severity=alert.severity,
        remediation_type="automatic",
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
            "environment": server.environment,
            "provider": server.provider,
            "alert_name": alert.alert_name,
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
    from app.services.incidents import add_event

    add_event(incident, "detected", "Service unavailable")
    db.session.commit()
    return incident


def settle_cleared_alert(alert):
    """An investigation has no playbook. It resolves only after its alert has cleared."""
    if alert is None or alert.status != "resolved" or alert.server_id is None:
        return None
    incident = db.session.scalar(
        select(Incident).where(
            Incident.alert_id == alert.id,
            Incident.action_key == "investigate",
            Incident.status.in_(("open", "acknowledged")),
        )
    )
    if incident is None:
        return None
    server = db.session.get(Server, alert.server_id)
    return _resolve_incident(incident, server, alert, "alert cleared", "The reported condition cleared.")


def _open_investigation(server, alert):
    """Unknown cause stays open. No playbook and no approval request are created."""
    current = _current_incident(server.id, "investigate")
    if current is not None:
        return current
    incident = Incident(
        server_id=server.id,
        alert_id=alert.id,
        action_key="investigate",
        status="open",
        severity=alert.severity,
        remediation_type="manual",
        retry_count=0,
        manual_required=True,
        verification_failed=False,
        blocked=False,
        reason="manual_investigation",
        opened_at=utcnow(),
    )
    db.session.add(incident)
    db.session.commit()
    from app.services.incidents import add_event

    add_event(
        incident,
        "manual_investigation",
        "Cause was not identified. No remediation action was started.",
    )
    db.session.commit()
    _note_manual(
        alert,
        "investigate",
        (
            "Reason: manual investigation. MANUAL_REQUIRED. "
            f"{alert.alert_name} does not match a runbook, so no action was started."
        ),
    )
    return incident


def _resolve_incident(incident, server, alert, reason, message="Recovery confirmed"):
    if incident is None or incident.status in {"resolved", "closed"}:
        return None
    from app.services.incidents import add_event

    add_event(incident, "resolved", message, to_status="resolved")
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
    from app.services.incidents import release_work

    release_work(incident, "blocked", "SSH or WinRM was down.")
    db.session.commit()


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
        from app.services.incidents import release_work

        release_work(incident, "execution_failed", "Retry limit reached.")
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


def _hold_for_plan(server, alert, incident, plan):
    """Stop a repeat of the previous action when the shared map now says something else."""
    from app.services.incidents import release_work

    if plan["blocked"]:
        if incident is not None:
            _mark_blocked(incident, server, alert, incident.action_key, plan["refusal"] or {})
        return
    if plan.get("action_key") and incident is not None and plan["action_key"] != incident.action_key:
        release_work(
            incident,
            "blocked",
            "Docker is inactive, so the container restart was not repeated.",
        )
        if action_risk(plan["action_key"]) == "medium":
            from app.services.approval import open_request

            open_request(server, plan["action_key"], plan["parameters"], _auto_actor(), None if alert is None else alert.id)
        db.session.commit()
        return
    if incident is not None:
        release_work(incident, "manual_investigation", "Cause was not identified. No remediation action was started.")
        db.session.commit()


def _start_auto(server, alert, suggestion, incident, retry_of=None):
    action_key = suggestion["action_key"]
    plan = resolve_plan(server, alert, requested_action=action_key)
    if plan["blocked"] or plan["investigate"] or plan.get("action_key") != action_key:
        _hold_for_plan(server, alert, incident, plan)
        return None
    if action_risk(action_key) == "high":
        _note_manual(
            alert,
            action_key,
            (
                f"Reason: risk. MANUAL_REQUIRED. {action_key} is HIGH. "
                "An admin must request and approve it. Auto-remediation did not run."
            ),
        )
        return None
    if action_risk(action_key) != "low":
        from app.services.approval import open_request

        open_request(server, action_key, plan.get("parameters") or suggestion["parameters"], _auto_actor(), alert.id)
        _note_manual(
            alert,
            action_key,
            f"Reason: risk. MANUAL_REQUIRED. {action_key} is {action_risk(action_key)} risk, so auto-remediation did not run.",
        )
        return None
    attempt = (incident.retry_count or 0) + 1
    details = _trace(
        server,
        action_key,
        "RUNNING",
        f"Auto-remediation requested {action_key}.",
        alert_id=alert.id,
        alert_name=alert.alert_name,
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
    from app.services.incidents import enter_progress

    enter_progress(
        incident,
        f"{action_key} started.",
        job_id=job.id,
        retry=retry_of is not None,
    )
    db.session.commit()
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
        alert_name=alert.alert_name,
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
            from app.services.incidents import release_work

            release_work(incident, "blocked", "SSH or WinRM was down.", job_id=job.id)
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
            from app.services.incidents import release_work

            release_work(incident, "verification_failed", "Post-check failed.", job_id=job.id)
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
        from app.services.incidents import note_result

        note_result(incident, "execution_failed", "Remediation command failed.", job_id=job.id)
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
        from app.services.incidents import release_work

        release_work(incident, "execution_failed", "Retry limit reached.", job_id=job.id)
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


def _service_already_up(server, action_key):
    """A stuck firing alert must not restart a service that is already answering."""
    if current_app.config.get("AUTOMATION_EXECUTOR") != "ansible":
        return False, ""
    checker = current_app.config.get("RECOVERY_CHECK")
    if checker is not None:
        ok, detail = checker(server, action_key)
        return bool(ok), detail or ""
    from app.services.checks import service_probe
    from app.services.probes import http_recovery, tcp_probe

    spec = service_probe(server, action_key)
    if spec is None:
        return False, ""
    kind, target, label = spec
    if kind == "http":
        ok, detail = http_recovery(target, timeout=2)
    else:
        host, port = target
        ok, latency = tcp_probe(host, port, timeout=2)
        detail = None if latency is None else f"{latency} ms"
    if not ok:
        return False, ""
    return True, f"{label} is up ({detail})."


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
            "Skipped because duplicate job already exists. "
            f"Job {same_action} for this server and action is already queued or running."
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
            "Skipped because duplicate job already exists. "
            f"Job {same_alert} for this alert is already queued or running."
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
            "alert_name": alert.alert_name,
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
        started = _aware(getattr(alert, "starts_at", None))
        noted = _aware(previous.created_at)
        if started is None or noted is None or noted >= started:
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
