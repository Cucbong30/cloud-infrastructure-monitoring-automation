"""MEDIUM and HIGH actions stop here. The playbook runs only after approval."""

import json
from datetime import timedelta

from flask import current_app
from sqlalchemy import select

from app.executors.actions import SERVICE_LABELS, action_risk
from app.extensions import db
from app.models import ApprovalRequest, AutomationJob, utcnow
from app.services.audit import record

PENDING = "PENDING_APPROVAL"
APPROVED = "APPROVED"
REJECTED = "REJECTED"
EXPIRED = "APPROVAL_EXPIRED"


class ApprovalPending(Exception):
    def __init__(self, approval):
        super().__init__(PENDING)
        self.request = approval


class ApprovalForbidden(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def approval_required(action_key):
    return action_risk(action_key) != "low"


def can_request(actor, action_key):
    """Viewer cannot request. Operator can request LOW and MEDIUM. Only admin can request HIGH."""
    role = getattr(actor, "role", None)
    risk = action_risk(action_key)
    if role == "admin":
        return True
    if role == "operator":
        return risk in {"low", "medium"}
    return False


def can_decide(actor, approval):
    """Only an admin decides MEDIUM and HIGH. Operator cannot approve."""
    role = getattr(actor, "role", None)
    return bool(
        approval is not None
        and role == "admin"
        and approval.status == PENDING
        and approval.risk in {"MEDIUM", "HIGH"}
    )


def expire_pending():
    now = utcnow()
    rows = db.session.scalars(
        select(ApprovalRequest).where(
            ApprovalRequest.status == PENDING,
            ApprovalRequest.expires_at <= now,
        )
    ).all()
    for approval in rows:
        approval.status = EXPIRED
        approval.decision = EXPIRED
        approval.decision_at = now
        approval.final_status = EXPIRED
        approval.execution_result = "NOT_RUN"
        approval.verification_result = "NOT_RUN"
        db.session.commit()
        record("approval.expired", "approval_request", approval.id, _facts(approval, "APPROVAL_EXPIRED"), system=True)
    return rows


def open_request(server, action_key, parameters, actor, alert_id=None):
    expire_pending()
    current = db.session.scalar(
        select(ApprovalRequest)
        .where(
            ApprovalRequest.server_id == server.id,
            ApprovalRequest.action_key == action_key,
            ApprovalRequest.status == PENDING,
        )
        .order_by(ApprovalRequest.id.desc())
    )
    if current is not None:
        return current
    name, role = _identity(actor)
    now = utcnow()
    minutes = int(current_app.config.get("APPROVAL_TIMEOUT_MINUTES", 5))
    approval = ApprovalRequest(
        server_id=server.id,
        alert_id=alert_id,
        requester_id=getattr(actor, "id", None),
        action_key=action_key,
        service=SERVICE_LABELS.get(action_key, action_key),
        risk=action_risk(action_key).upper(),
        parameters_json=json.dumps(parameters or {}, sort_keys=True),
        mode="AUTO" if (role or "").upper() == "SYSTEM" else "MANUAL",
        status=PENDING,
        requester_name=name,
        requester_role=role or "unknown",
        final_status=PENDING,
        execution_result="NOT_RUN",
        verification_result="NOT_RUN",
        requested_at=now,
        expires_at=now + timedelta(minutes=max(minutes, 0)),
    )
    db.session.add(approval)
    db.session.commit()
    record(
        "approval.requested",
        "approval_request",
        approval.id,
        _facts(approval, "Approval requested. The playbook was not started."),
        user_id=getattr(actor, "id", None),
    )
    return approval


def decide(request_id, actor, decision, reason=""):
    expire_pending()
    approval = db.session.get(ApprovalRequest, request_id)
    if approval is None or approval.status != PENDING:
        raise ApprovalForbidden("This approval request is no longer pending.")
    if not can_decide(actor, approval):
        message = _denial_message(actor, approval)
        record(
            "permission.denied",
            "approval_request",
            approval.id,
            _facts(approval, message, decision="DENIED"),
            user_id=getattr(actor, "id", None),
        )
        raise ApprovalForbidden(message)
    now = utcnow()
    name, role = _identity(actor)
    approval.approver_id = getattr(actor, "id", None)
    approval.approver_name = name
    approval.approver_role = role
    approval.decision_at = now
    if decision == REJECTED:
        approval.status = REJECTED
        approval.decision = REJECTED
        approval.decision_reason = (reason or "Rejected.").strip()[:200]
        approval.final_status = REJECTED
        approval.execution_result = "NOT_RUN"
        approval.verification_result = "NOT_RUN"
        db.session.commit()
        record(
            "approval.rejected",
            "approval_request",
            approval.id,
            _facts(approval, approval.decision_reason),
            user_id=getattr(actor, "id", None),
        )
        return approval
    approval.status = APPROVED
    approval.decision = APPROVED
    approval.decision_reason = None
    db.session.commit()
    record(
        "approval.approved",
        "approval_request",
        approval.id,
        _facts(approval, "Approved. Remediation can start."),
        user_id=getattr(actor, "id", None),
    )
    from app.services.remediation import trigger_manual_remediation

    parameters = json.loads(approval.parameters_json or "{}")
    job = trigger_manual_remediation(
        approval.server,
        approval.action_key,
        parameters,
        actor,
        alert_id=approval.alert_id,
        approval_request=approval,
    )
    approval.job_id = job.id
    approval.incident_id = job.incident_id
    approval.execution_started_at = job.started_at or job.created_at
    approval.execution_result, approval.verification_result = _results(job)
    approval.final_status = job.final_status or job.status
    db.session.commit()
    record(
        "approval.completed",
        "approval_request",
        approval.id,
        _facts(approval, f"Final status {approval.final_status}."),
        user_id=getattr(actor, "id", None),
    )
    return approval


def _request_url(request_id):
    base = (current_app.config.get("PORTAL_BASE_URL") or "").strip().rstrip("/")
    if not base:
        redirect_uri = current_app.config.get("ENTRA_REDIRECT_URI") or ""
        if "://" in redirect_uri:
            from urllib.parse import urlsplit

            parts = urlsplit(redirect_uri)
            base = f"{parts.scheme}://{parts.netloc}"
    if not base:
        base = "http://localhost:5000"
    return f"{base}/automation/approvals/{request_id}"


def _requester_email(approval):
    stored = ((getattr(getattr(approval, "requester", None), "email", None) or "")).strip()
    if "@" in stored:
        return stored
    name = (approval.requester_name or "").strip()
    return name if "@" in name else ""


def _identity(actor):
    email = ((getattr(actor, "email", None) or "")).strip()
    name = email or getattr(actor, "username", None) or "unknown"
    return name, getattr(actor, "role", None)


def _denial_message(actor, approval):
    role = (getattr(actor, "role", None) or "unknown").capitalize()
    return f"Permission denied for {role} role"


def _results(job):
    kind = getattr(job, "verification_result", None)
    if kind in {"passed", "failed"}:
        execution = "SUCCESS"
    elif kind == "blocked":
        execution = "NOT_RUN"
    elif kind == "skipped" and getattr(job, "status", None) == "failed":
        execution = "FAILED"
    else:
        execution = "NOT_RUN"
    verification = {"passed": "PASSED", "failed": "FAILED", "blocked": "NOT_RUN", "skipped": "SKIPPED"}.get(
        kind, "NOT_RUN"
    )
    return execution, verification


def _facts(approval, message, decision=None):
    server_name = approval.server.name if approval.server is not None else "—"
    job = db.session.get(AutomationJob, approval.job_id) if approval.job_id else None
    return {
        "request_id": approval.id,
        "requester": approval.requester_name,
        "requester_role": approval.requester_role,
        "approver": approval.approver_name or "—",
        "approver_role": approval.approver_role or "—",
        "target": server_name,
        "service": approval.service,
        "action": approval.action_key,
        "action_key": approval.action_key,
        "risk": approval.risk,
        "request_url": _request_url(approval.id),
        "requester_email": _requester_email(approval),
        "requested_at": approval.requested_at,
        "decision": decision or approval.decision or approval.status,
        "decision_time": approval.decision_at,
        "execution_started_at": approval.execution_started_at,
        "execution_result": approval.execution_result or "NOT_RUN",
        "verification_result": approval.verification_result or "NOT_RUN",
        "final_status": approval.final_status or approval.status,
        "result": approval.final_status or approval.status,
        "job_id": approval.job_id,
        "incident_id": approval.incident_id or (None if job is None else job.incident_id),
        "mode": approval.mode or "MANUAL",
        "triggered_by": approval.requester_name,
        "user_role": approval.requester_role,
        "reason": approval.decision_reason or message,
        "message": message,
        "playbook_executed": bool(approval.job_id) and approval.execution_result not in {None, "NOT_RUN"},
    }
