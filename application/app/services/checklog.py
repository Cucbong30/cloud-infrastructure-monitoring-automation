"""Append a log line only when a check changes, including the return to UP."""

from sqlalchemy import select

from app.extensions import db
from app.models import AuditLog
from app.services.audit import record


def observe_hosts(hosts):
    for host in hosts or []:
        name = (host.get("name") or "").upper()
        if not name:
            continue
        _observe(name, "exporter", host.get("exporter_label") or "exporter", host.get("exporter"))
        for service in host.get("services") or []:
            _observe(name, f"service:{service.get('name')}", service.get("name"), service.get("status"))
        management = host.get("management") or None
        if management:
            label = f"{management.get('label')} :{management.get('port')}"
            _observe(name, "management", label, management.get("status"), kind="management")


def _observe(name, key, label, status, kind="check"):
    if status not in {"UP", "DOWN"} or not label:
        return
    resource_id = f"{name}:{key}"[:64]
    last = db.session.scalar(
        select(AuditLog)
        .where(AuditLog.resource_type == "check", AuditLog.resource_id == resource_id)
        .order_by(AuditLog.id.desc())
    )
    action = "check.up" if status == "UP" else "check.down"
    if last is not None and last.action == action:
        return
    state = "up" if status == "UP" else "down"
    record(
        action,
        "check",
        resource_id,
        {
            "host": name,
            "check": label,
            "status": status,
            "kind": kind,
            "message": f"{name} {label} is {state}",
        },
        system=True,
    )
