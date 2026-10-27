from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models import AutomationJob, Server
from app.services.audit import record
from app.services.automation import AutomationRejected, dispatch, enqueue_job
from app.services.metrics import HOST_CHECKS

LAB_ACTIONS = {
    "WEB01": ("restart_nginx", {}, "Restart Nginx"),
    "APP01": ("restart_container", {"container_name": "app01-web"}, "Restart container"),
    "WIN01": ("restart_windows_exporter", {"service_name": "windows_exporter"}, "Restart Windows Exporter"),
}
ALERTS_FOR = {
    "WEB01": {"service_down", "InstanceDown", "NginxDown"},
    "APP01": {"container_down", "service_down"},
    "WIN01": {"service_down", "InstanceDown", "WindowsExporterDown"},
}


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
    if blocked_reason(server, alert):
        return None
    spec = LAB_ACTIONS.get((server.name or "").upper())
    if spec is None:
        return None
    if alert is not None and alert.alert_name not in ALERTS_FOR.get(server.name.upper(), set()):
        return None
    action_key, parameters, label = spec
    return {"action_key": action_key, "parameters": dict(parameters), "label": label}


def maybe_remediate(alert):
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return None
    if alert.status != "firing" or alert.server_id is None:
        return None
    server = db.session.get(Server, alert.server_id)
    suggestion = suggest_remediation(server, alert)
    if suggestion is None:
        return None
    action_key = suggestion["action_key"]
    existing = db.session.scalar(
        select(AutomationJob.id).where(
            AutomationJob.alert_id == alert.id,
            AutomationJob.action_key == action_key,
            AutomationJob.status.in_(("queued", "running", "succeeded")),
        )
    )
    if existing is not None:
        return None
    record(
        "remediation.request",
        "alert",
        alert.id,
        {"action_key": action_key, "alert_id": alert.id},
    )
    try:
        job = enqueue_job(
            server_id=server.id,
            action_key=action_key,
            parameters=suggestion["parameters"],
            trigger_source="remediation",
            requested_by=None,
            alert_id=alert.id,
        )
        return dispatch(job.id, actor=None)
    except AutomationRejected:
        current_app.logger.info("Remediation skipped")
        return None
