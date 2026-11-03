from datetime import timezone

from flask import Blueprint, abort, current_app, jsonify, render_template, url_for
from flask_login import current_user
from sqlalchemy import func, or_, select

from app.extensions import db
from app.models import Alert, AuditLog, AutomationJob, Server
from app.presentation import audit_message, format_clock, job_outcome_label, verification_label
from app.services.checklog import observe_hosts
from app.services.checks import ACTION_CHANNELS, MANAGEMENT_CHANNELS, management_status
from app.services.inventory import LAB_TARGETS, canonical_server_name
from app.services.metrics import collect_metrics
from app.services.remediation import LAB_ACTIONS, suggest_remediation, unreachable_message
from app.services.prometheus import client_from_app

bp = Blueprint("dashboard", __name__)


@bp.get("/dashboard")
def index():
    return render_template("dashboard.html", **_dashboard_context())


@bp.get("/dashboard/snapshot")
def snapshot():
    return jsonify(_dashboard_payload())


@bp.get("/dashboard/events/<name>")
def events(name):
    name = name.upper()
    if name not in LAB_TARGETS:
        abort(404)
    payload = _dashboard_payload()
    host = next((item for item in payload["hosts"] if item["name"] == name), None)
    if host is None:
        abort(404)
    server = db.session.scalar(select(Server).where(Server.name == name))
    if server is not None:
        channel = management_status(server)
        if channel is not None:
            host["management"] = channel
    return jsonify(
        {
            "host": host,
            "backend": {
                "available": payload["prometheus_available"],
                "message": payload["prometheus_message"],
            },
            "events": _host_events(name, host),
        }
    )


def _dashboard_context():
    return _dashboard_payload()


def _dashboard_payload():
    metrics, hosts, prometheus = collect_metrics()
    servers = {server.name: server for server in db.session.scalars(select(Server))}
    for host in hosts:
        server = servers.get(host["name"])
        if server is not None:
            host["server_id"] = server.id
            host["href"] = url_for("servers.detail", server_id=server.id)
            host["last_seen"] = _iso(server.last_seen_at)
            host["ip"] = server.ip_address
            channel = management_status(server)
            if channel is not None:
                host["management"] = channel
        else:
            host["href"] = url_for("servers.index")
            host["last_seen"] = _iso(host.get("last_seen_at"))
        host.pop("last_seen_at", None)
        _annotate_problem(host)
    observe_hosts(hosts)

    lab_names = set(LAB_TARGETS)
    firing = [
        alert
        for alert in db.session.scalars(
            select(Alert)
            .where(Alert.status.in_(("firing", "acknowledged")))
            .order_by(Alert.starts_at.desc())
        )
        if alert.server and alert.server.name in lab_names
    ][:8]
    resolved_count = db.session.scalar(select(func.count()).where(Alert.status == "resolved")) or 0
    lab_counts = {"Healthy": 0, "Degraded": 0, "Unreachable": 0}
    for host in hosts:
        lab_counts[host["status"]] = lab_counts.get(host["status"], 0) + 1
    services = _flatten_services(hosts)
    down_services = sum(1 for item in services if item["status"] == "DOWN")
    issues = _live_issues(hosts)
    return {
        "metrics": metrics,
        "hosts": hosts,
        "services": services,
        "issues": issues,
        "prometheus_available": prometheus.available,
        "prometheus_message": prometheus.message or "",
        "kpis": {
            "servers": len(hosts),
            "healthy": lab_counts.get("Healthy", 0),
            "online": lab_counts.get("Healthy", 0),
            "degraded": lab_counts.get("Degraded", 0),
            "unreachable": lab_counts.get("Unreachable", 0),
            "firing_alerts": len(firing),
            "resolved_alerts": resolved_count,
            "down_services": down_services,
        },
        "alerts": [
            {
                "id": alert.id,
                "name": alert.alert_name,
                "severity": alert.severity,
                "status": alert.status,
                "summary": alert.summary,
                "starts_at": _iso(alert.starts_at),
                "server": alert.server.name if alert.server else None,
            }
            for alert in firing
        ],
        "grafana_url": current_app.config.get("GRAFANA_BASE_URL", "") if current_user.role == "admin" else "",
    }


def _annotate_problem(host):
    if host.get("status") == "Unreachable":
        host["problem_ok"] = False
        host["problem"] = unreachable_message(host["name"])
        return
    parts = []
    if host.get("exporter") == "DOWN":
        parts.append(f"{host['exporter_label']} is down")
    for service in host.get("services") or []:
        if service.get("status") == "DOWN":
            parts.append(f"{service['name']} is down")
    host["problem_ok"] = not parts
    host["problem"] = "All checks OK" if not parts else "; ".join(parts)


def _live_issues(hosts):
    issues = []
    for host in hosts:
        if host.get("exporter") == "DOWN":
            issues.append({"host": host["name"], "detail": f"{host['exporter_label']} is down"})
        for service in host.get("services") or []:
            if service.get("status") == "DOWN":
                issues.append({"host": host["name"], "detail": f"{service['name']} is down"})
    return issues


def _flatten_services(hosts):
    rows = []
    for host in hosts:
        rows.append(
            {
                "host": host["name"],
                "name": host["exporter_label"],
                "short": host["exporter_short"],
                "kind": "agent",
                "status": host["exporter"],
                "latency_ms": None,
            }
        )
        for service in host["services"]:
            rows.append(
                {
                    "host": host["name"],
                    "name": service["name"],
                    "short": service["short"],
                    "kind": "service",
                    "status": service["status"],
                    "latency_ms": service.get("latency_ms"),
                }
            )
    return rows


def _host_events(name, host):
    events = []
    if host.get("status") == "Unreachable":
        events.append(
            {
                "source": "probe",
                "level": "error",
                "title": "Host unreachable",
                "message": unreachable_message(name),
                "at": host.get("last_seen"),
            }
        )
    else:
        if host.get("exporter") == "DOWN":
            events.append(
                {
                    "source": "probe",
                    "level": "error",
                    "title": host["exporter_label"],
                    "message": f"{host['exporter_label']} is DOWN. Host metrics come from {host['instance']}.",
                    "at": host.get("last_seen"),
                }
            )
        for service in host.get("services") or []:
            if service.get("status") == "DOWN":
                latency = f" Last probe {service['latency_ms']} ms." if service.get("latency_ms") is not None else ""
                events.append(
                    {
                        "source": "probe",
                        "level": "error",
                        "title": service["name"],
                        "message": f"{host['name']} {service['name']} is DOWN.{latency}",
                        "at": host.get("last_seen"),
                    }
                )
    server = db.session.scalar(select(Server).where(Server.name == name))
    if server is not None:
        channel = management_status(server)
        block_notice = None
        if channel and channel.get("status") == "DOWN":
            block_notice = (
                f"Remediation unavailable. {name} management channel "
                f"{channel['label']} :{channel['port']} is down."
            )
        for row in db.session.scalars(
            select(AuditLog)
            .where(AuditLog.resource_type == "check", AuditLog.resource_id.like(f"{name}:%"))
            .order_by(AuditLog.created_at.desc())
            .limit(30)
        ):
            events.append(_check_event(row))
        for alert in db.session.scalars(
            select(Alert).where(Alert.server_id == server.id).order_by(Alert.starts_at.desc()).limit(12)
        ):
            suggestion = suggest_remediation(server, alert)
            notice = None
            if suggestion and block_notice:
                notice = block_notice
            elif suggestion:
                notice = f"Suggested action: {suggestion['label']}"
            events.append(
                {
                    "source": "alert",
                    "level": alert.severity,
                    "title": alert.alert_name,
                    "message": alert.description or alert.summary or alert.alert_name,
                    "notice": notice,
                    "href": url_for("alerts.index") + f"#alert-{alert.id}",
                    "jobs": [
                        {
                            "id": job.id,
                            "label": f"Job {job.id} {job_outcome_label(job)}",
                            "href": url_for("automation.detail", job_id=job.id),
                        }
                        for job in sorted(alert.jobs, key=lambda item: item.id, reverse=True)[:4]
                    ],
                    "at": _iso(alert.starts_at),
                }
            )
        for row in db.session.scalars(
            select(AuditLog)
            .where(
                AuditLog.resource_type != "check",
                or_(
                    AuditLog.resource_id == str(server.id),
                    AuditLog.details_json.contains(name),
                ),
            )
            .order_by(AuditLog.created_at.desc())
            .limit(12)
        ):
            events.append(
                {
                    "source": "audit",
                    "level": "info",
                    "title": row.action,
                    "message": row.details_json or row.action,
                    "at": _iso(row.created_at),
                }
            )
        for job in db.session.scalars(
            select(AutomationJob).where(AutomationJob.server_id == server.id).order_by(AutomationJob.created_at.desc()).limit(8)
        ):
            event = _job_event(job)
            event["href"] = url_for("automation.detail", job_id=job.id)
            if job.alert_id and job.alert is not None:
                event["alert_href"] = url_for("alerts.index") + f"#alert-{job.alert.id}"
                event["alert_name"] = job.alert.alert_name
            events.append(event)
    try:
        for alert in client_from_app().list_alerts():
            mapped = canonical_server_name(alert.instance)
            if mapped != name:
                continue
            events.append(
                {
                    "source": "prometheus",
                    "level": alert.severity or "warning",
                    "title": alert.alert_name,
                    "message": alert.description or alert.summary or alert.alert_name,
                    "at": None,
                }
            )
    except Exception:
        pass
    events.sort(key=lambda item: item.get("at") or "", reverse=True)
    for event in events:
        event["at_label"] = format_clock(event.get("at"))
    return events[:40]


def _check_event(row):
    data = {}
    try:
        import json

        parsed = json.loads(row.details_json or "{}")
        if isinstance(parsed, dict):
            data = parsed
    except (TypeError, json.JSONDecodeError):
        data = {}
    up = row.action == "check.up"
    kind = "management" if data.get("kind") == "management" else "check"
    title = data.get("message") or audit_message(row)
    detail = _management_detail(data.get("host"), data.get("check"), up) if kind == "management" else ""
    return {
        "source": kind,
        "level": "up" if up else "warning",
        "title": title,
        "message": detail,
        "at": _iso(row.created_at),
    }


def _management_detail(host, check, up):
    spec = LAB_ACTIONS.get(host or "")
    action_key = spec[0] if spec else "remediation"
    action_label = spec[2] if spec else "Remediation"
    channel = f"{host} management channel {check}"
    if up:
        return f"Remediation available. {channel} is up.\nAction: {action_key}. {action_label} can run."
    return f"Remediation unavailable. {channel} is down.\nAction: {action_key}. The playbook was not started."


def _job_event(job):
    """SSH connection failures are a management-channel block, not a playbook result."""
    reason = (getattr(job, "block_reason", None) or "").strip()
    output = getattr(job, "output_excerpt", None) or ""
    if not reason and _ssh_control_failure(output):
        target = ACTION_CHANNELS.get(getattr(job, "action_key", None))
        spec = MANAGEMENT_CHANNELS.get(target or "")
        if spec is not None:
            reason = f"{target} management channel {spec['label']} :{spec['port']} is down"
    label = verification_label(job)
    outcome = job_outcome_label(job)
    stderr = getattr(job, "stderr_excerpt", None) or ""
    log = "\n".join(part for part in (output, stderr) if part).strip()
    detail = getattr(job, "verification_detail", None) or ""
    exit_code = getattr(job, "exit_code", None)
    if reason:
        return {
            "source": "job",
            "level": "warning",
            "title": "Remediation unavailable",
            "message": reason,
            "log": log,
            "exit_code": exit_code,
            "verification_detail": detail,
            "job_id": getattr(job, "id", None),
            "verification": label or "Blocked",
            "outcome": outcome if getattr(job, "verification_result", None) else "Blocked",
            "can_retry": getattr(job, "status", None) == "failed",
            "at": _iso(job.created_at),
        }
    return {
        "source": "job",
        "level": "error" if job.status == "failed" else "info",
        "title": job.action_key,
        "message": detail or job.status,
        "log": log,
        "exit_code": exit_code,
        "verification_detail": detail,
        "job_id": getattr(job, "id", None),
        "verification": label,
        "outcome": outcome,
        "can_retry": job.status == "failed",
        "at": _iso(job.created_at),
    }


def _ssh_control_failure(output):
    text = output or ""
    return "No route to host" in text or "Failed to connect to the host via ssh" in text


def _iso(value):
    if not value:
        return None
    if getattr(value, "tzinfo", None) is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()
