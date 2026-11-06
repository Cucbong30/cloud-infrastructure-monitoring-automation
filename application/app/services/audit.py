import json

from flask import has_request_context, request
from flask_login import current_user

from app.extensions import db
from app.models import AuditLog, utcnow


def record(action, resource_type, resource_id=None, details=None, user_id=None, *, system=False):
    if not system and user_id is None and has_request_context() and current_user.is_authenticated:
        user_id = current_user.id
    payload_data = dict(details or {}) if isinstance(details, dict) else {}
    actor_name = "SYSTEM"
    role_name = "SYSTEM"
    if user_id is not None:
        from app.models import User

        actor = db.session.get(User, user_id)
        if actor is not None:
            actor_name = actor.username
            role_name = actor.role
    payload_data.setdefault("actor", actor_name)
    payload_data.setdefault("role", role_name)
    if "trigger" not in payload_data and payload_data.get("trigger_source"):
        payload_data["trigger"] = payload_data["trigger_source"]
    payload = json.dumps(payload_data, default=str, sort_keys=True)
    if len(payload) > 4000:
        payload = payload[:4000]
    ip_address = None
    if has_request_context() and request.remote_addr:
        ip_address = request.remote_addr[:45]
    entry = AuditLog(
        user_id=user_id,
        action=action[:80],
        resource_type=resource_type[:40],
        resource_id=None if resource_id is None else str(resource_id)[:64],
        details_json=payload,
        ip_address=ip_address,
        created_at=utcnow(),
    )
    db.session.add(entry)
    db.session.commit()
    try:
        from app.services.notify import notify_audit

        notify_audit(action, payload_data)
    except Exception:
        from flask import current_app

        current_app.logger.exception("Alert notification was not sent")
    return entry
