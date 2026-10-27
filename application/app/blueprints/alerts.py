from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.authz import roles_required
from app.extensions import db
from app.models import Alert, utcnow
from app.presentation import job_status_label
from app.services.audit import record
from app.services.automation import AutomationRejected, queue_and_dispatch
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
    blocked = {alert.id: blocked_reason(alert.server, alert) for alert in alerts}
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
    reason = blocked_reason(alert.server, alert)
    if reason:
        flash(reason, "warning")
        return redirect(url_for("alerts.index"))
    suggestion = suggest_remediation(alert.server, alert)
    if suggestion is None:
        abort(400)
    try:
        job = queue_and_dispatch(
            server_id=alert.server.id,
            action_key=suggestion["action_key"],
            parameters=suggestion["parameters"],
            actor=current_user,
            alert_id=alert.id,
        )
    except AutomationRejected:
        flash("Remediation was rejected.", "warning")
        return redirect(url_for("alerts.index"))
    flash(
        f"Remediation job {job.id} finished with status {job_status_label(job.status)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("automation.index"))
