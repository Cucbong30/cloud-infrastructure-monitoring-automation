from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.authz import roles_required
from app.executors.actions import SERVICE_LABELS, action_risk, target_spec
from app.extensions import db
from app.models import ApprovalRequest, Incident, Server
from app.presentation import job_outcome_label
from app.services.approval import PENDING, ApprovalForbidden, ApprovalPending, can_request
from app.services.audit import record
from app.services.automation import AutomationRejected, RemediationUnavailable
from app.services.incidents import IncidentTransitionError, acknowledge, close
from app.services.remediation import actions_for, resolve_plan, trigger_manual_remediation
from app.services.runbooks import action_runbook, mapped_actions, runbook_for

bp = Blueprint("incidents", __name__, url_prefix="/incidents")

STATUSES = ("open", "acknowledged", "in_progress", "resolved", "closed")
SEVERITIES = ("critical", "warning", "info")


@bp.get("/")
def index():
    status = request.args.get("status", "")
    severity = request.args.get("severity", "")
    target = request.args.get("target", "")
    if status not in STATUSES:
        status = ""
    if severity not in SEVERITIES:
        severity = ""
    query = select(Incident).order_by(Incident.opened_at.desc(), Incident.id.desc()).limit(100)
    if status:
        query = query.where(Incident.status == status)
    if severity:
        query = query.where(Incident.severity == severity)
    if target.isdigit():
        query = query.where(Incident.server_id == int(target))
    incidents = db.session.scalars(query).all()
    servers = db.session.scalars(select(Server).where(Server.is_active.is_(True)).order_by(Server.name)).all()
    return render_template(
        "incidents/list.html",
        incidents=incidents,
        servers=servers,
        status=status,
        severity=severity,
        target=target,
    )


@bp.get("/<int:incident_id>")
def detail(incident_id):
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)
    events = sorted(incident.events, key=lambda item: (item.created_at, item.id))
    jobs = sorted(incident.jobs, key=lambda item: item.id, reverse=True)
    approvals = db.session.scalars(
        select(ApprovalRequest)
        .where(ApprovalRequest.incident_id == incident.id)
        .order_by(ApprovalRequest.id.desc())
    ).all()
    latest_job = jobs[0] if jobs else None
    label, risk = _action_context(incident)
    pending = next((item for item in approvals if item.status == PENDING), None)
    failure = None if latest_job is None else runbook_for(incident.action_key, latest_job.final_status or "")
    choices, cause = _remediation_choices(incident)
    selected = next((item for item in choices if item["selected"]), None)
    can_act = (
        current_user.role in {"operator", "admin"}
        and incident.status in {"open", "acknowledged"}
        and pending is None
        and not incident.blocked
    )
    return render_template(
        "incidents/detail.html",
        incident=incident,
        events=events,
        jobs=jobs,
        approvals=approvals,
        latest_job=latest_job,
        action_label=label,
        risk=risk,
        approval_required=risk in {"medium", "high"},
        pending_approval=pending,
        can_request_action=can_request(current_user, incident.action_key),
        runbook=action_runbook(incident.action_key),
        failure_runbook=failure,
        choices=choices,
        cause_label=cause,
        selected_action=selected,
        show_action_form=can_act and selected is not None,
        high_locked=can_act and any(item["risk"] == "high" and not item["allowed"] for item in choices),
    )


@bp.post("/<int:incident_id>/acknowledge")
@roles_required("operator", "admin")
def acknowledge_incident(incident_id):
    incident = _active_incident(incident_id)
    try:
        acknowledge(incident, current_user)
    except IncidentTransitionError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("incidents.detail", incident_id=incident.id))
    db.session.commit()
    _audit(incident, "incident.acknowledged", "ACKNOWLEDGED", "Incident acknowledged.")
    flash("Incident acknowledged.", "success")
    return redirect(url_for("incidents.detail", incident_id=incident.id))


@bp.post("/<int:incident_id>/close")
@roles_required("operator", "admin")
def close_incident(incident_id):
    incident = _active_incident(incident_id)
    try:
        close(incident, current_user, request.form.get("reason") or "")
    except IncidentTransitionError as exc:
        flash(str(exc), "warning")
        return redirect(url_for("incidents.detail", incident_id=incident.id))
    db.session.commit()
    _audit(incident, "incident.closed", "CLOSED", "Incident closed.")
    flash("Incident closed. The job history was kept.", "success")
    return redirect(url_for("incidents.detail", incident_id=incident.id))


@bp.post("/<int:incident_id>/remediate")
@roles_required("operator", "admin")
def remediate(incident_id):
    incident = _active_incident(incident_id)
    if incident.status not in {"open", "acknowledged"}:
        abort(400)
    server = incident.server
    if server is None:
        abort(404)
    catalog = {item["action_key"] for item in mapped_actions(server.name)}
    chosen = (request.form.get("action_key") or "").strip() or incident.action_key
    if chosen not in catalog:
        abort(400)
    if not can_request(current_user, chosen):
        abort(403)
    spec = target_spec(server.name, chosen)
    parameters = {} if spec is None else dict(spec[1])
    try:
        job = trigger_manual_remediation(
            server,
            chosen,
            parameters,
            current_user,
            alert_id=incident.alert_id,
            bound_incident=incident,
        )
    except ApprovalPending as pending:
        flash(
            f"Approval request {pending.request.id} is PENDING_APPROVAL. The playbook was not started.",
            "warning",
        )
        return redirect(url_for("incidents.detail", incident_id=pending.request.incident_id or incident.id))
    except ApprovalForbidden:
        abort(403)
    except (AutomationRejected, RemediationUnavailable) as exc:
        flash(getattr(exc, "reason", None) or str(exc), "warning")
        return redirect(url_for("incidents.detail", incident_id=incident.id))
    flash(
        job.block_reason or f"Remediation job {job.id} finished with status {job_outcome_label(job)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("incidents.detail", incident_id=incident.id))


_CAUSE_LABELS = {
    "nginx_down": "Nginx down",
    "container_down": "Container down",
    "docker_service_down": "Docker service down",
    "exporter_down": "Windows exporter down",
    "reboot_required": "Reboot required",
    "unknown_issue": "Unknown",
    "management_unavailable": "Management unavailable",
}


def _remediation_choices(incident):
    """Actions this target allows. The cause check preselects one; risk and role decide who can send it."""
    server = incident.server
    if server is None:
        return [], None
    requested = None if incident.action_key in {"investigate", "blocked"} else incident.action_key
    plan = resolve_plan(server, incident.alert, requested_action=requested)
    recommended = plan.get("action_key")
    choices = []
    for item in mapped_actions(server.name):
        choices.append(
            {
                **item,
                "allowed": can_request(current_user, item["action_key"]),
                "recommended": item["action_key"] == recommended,
                "selected": False,
            }
        )
    selected = next((item for item in choices if item["allowed"] and item["recommended"]), None)
    if selected is None:
        selected = next((item for item in choices if item["allowed"]), None)
    if selected is not None:
        selected["selected"] = True
    return choices, _CAUSE_LABELS.get(plan.get("incident_type"), plan.get("incident_type"))


def _action_context(incident):
    if incident.action_key == "investigate":
        return "Manual investigation", ""
    if incident.action_key == "blocked":
        return "Block remediation", ""
    server_name = incident.server.name if incident.server is not None else ""
    match = next((item for item in actions_for(server_name) if item[0] == incident.action_key), None)
    label = match[2] if match is not None else SERVICE_LABELS.get(incident.action_key, incident.action_key)
    return label, action_risk(incident.action_key)


def _active_incident(incident_id):
    incident = db.session.get(Incident, incident_id)
    if incident is None:
        abort(404)
    return incident


def _audit(incident, action, result, message):
    server = incident.server
    record(
        action,
        "incident",
        incident.id,
        {
            "message": message,
            "result": result,
            "action": incident.action_key,
            "action_key": incident.action_key,
            "target": None if server is None else server.name,
            "incident_id": incident.id,
            "alert_id": incident.alert_id,
            "mode": "MANUAL",
            "trigger": "manual",
        },
        user_id=current_user.id,
    )
