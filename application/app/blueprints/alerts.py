from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.authz import roles_required
from app.extensions import db
from app.models import Alert, utcnow
from app.presentation import job_outcome_label
from app.services.audit import record
from app.services.automation import AutomationRejected, RemediationUnavailable, queue_and_dispatch
from app.services.checks import management_block
from app.services.remediation import blocked_reason, suggest_remediation

bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@bp.get("/")
def index():
    severity = request.args.get("severity", "")
    status = request.args.get("status", "")
    if severity not in {"critical", "warning", "info"}:
        severity = ""
    if status not in {"firing", "acknowledged", "resolved"}:
        status = ""
    query = select(Alert).order_by(Alert.created_at.desc()).limit(100)
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    alerts = db.session.scalars(query).all()
    suggestions = {alert.id: suggest_remediation(alert.server, alert) for alert in alerts}
    server_blocks = {}
    blocked = {}
    for alert in alerts:
        server = alert.server
        if server is None:
            blocked[alert.id] = None
            continue
        if server.id not in server_blocks:
            server_blocks[server.id] = management_block(server)
        blocked[alert.id] = server_blocks[server.id] if suggestions.get(alert.id) else None
    return render_template(
        "alerts/list.html",
        alerts=alerts,
        severity=severity,
        status=status,
        suggestions=suggestions,
        blocked=blocked,
    )


@bp.post("/<int:alert_id>/acknowledge")
@roles_required("operator", "admin")
def acknowledge(alert_id):
    alert = db.session.get(Alert, alert_id)
    if alert is None:
        abort(404)
    if alert.status != "firing":
        abort(400)
    alert.status = "acknowledged"
    alert.acknowledged_by = current_user.id
    alert.acknowledged_at = utcnow()
    db.session.commit()
    record(
        "alert.acknowledge",
        "alert",
        alert.id,
        {"fingerprint": alert.fingerprint, "alert_name": alert.alert_name},
        user_id=current_user.id,
    )
    flash("Alert acknowledged.", "success")
    return redirect(url_for("alerts.index"))


@bp.post("/<int:alert_id>/remediate")
@roles_required("operator", "admin")
def remediate(alert_id):
    alert = db.session.get(Alert, alert_id)
    if alert is None or alert.server is None:
        abort(404)
    if alert.status == "resolved":
        abort(400)
    suggestion = suggest_remediation(alert.server, alert)
    if suggestion is None:
        abort(400)
    if blocked_reason(alert.server, alert) and management_block(alert.server) is None:
        flash(blocked_reason(alert.server, alert), "warning")
        return redirect(url_for("alerts.index"))
    try:
        job = queue_and_dispatch(
            server_id=alert.server.id,
            action_key=suggestion["action_key"],
            parameters=suggestion["parameters"],
            actor=current_user,
            alert_id=alert.id,
            trigger_source="remediation",
        )
    except RemediationUnavailable as exc:
        flash(exc.reason, "warning")
        return redirect(url_for("alerts.index"))
    except AutomationRejected:
        flash("Remediation was rejected.", "warning")
        return redirect(url_for("alerts.index"))
    flash(
        job.block_reason or f"Remediation job {job.id} finished with status {job_outcome_label(job)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("automation.detail", job_id=job.id))
