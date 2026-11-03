from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.authz import roles_required
from app.executors.actions import ACTIONS, LAB_TARGETS
from app.extensions import db
from app.forms import JobForm
from app.models import AuditLog, AutomationJob, Server
from app.presentation import job_outcome_label
from app.services.automation import (
    REJECTED_PARAMETER_KEYS,
    AutomationRejected,
    RemediationUnavailable,
    queue_and_dispatch,
    retry_job,
)
from app.services.checks import management_block, management_status
from app.services.remediation import LAB_ACTIONS, blocked_reason

bp = Blueprint("automation", __name__, url_prefix="/automation")

FORM_KEYS = {
    "csrf_token",
    "server_id",
    "action_key",
    "service_name",
    "container_name",
    "path",
    "simulate",
    "submit",
}


def _prepare_form():
    form = JobForm()
    servers = db.session.scalars(select(Server).where(Server.is_active.is_(True)).order_by(Server.name)).all()
    form.server_id.choices = [(server.id, f"{server.name} ({server.environment})") for server in servers]
    return form


@bp.get("/")
def index():
    jobs = db.session.scalars(select(AutomationJob).order_by(AutomationJob.created_at.desc()).limit(100)).all()
    form = _prepare_form()
    notices = []
    blocks = {}
    for server in db.session.scalars(select(Server).where(Server.is_active.is_(True)).order_by(Server.name)):
        if (server.name or "").upper() not in LAB_ACTIONS:
            continue
        channel = management_status(server)
        reason = management_block(server) or blocked_reason(server)
        if reason:
            prefix = f"{server.name}: " if channel and channel.get("status") == "DOWN" else ""
            notices.append(f"{prefix}{reason}")
        if reason:
            blocks[str(server.id)] = reason
    return render_template(
        "automation/list.html",
        jobs=jobs,
        form=form,
        actions=ACTIONS,
        unreachable_notices=notices,
        management_blocks=blocks,
    )


@bp.post("/jobs")
@roles_required("operator", "admin")
def create_job():
    if REJECTED_PARAMETER_KEYS & set(request.form.keys()):
        abort(400)
    if set(request.form.keys()) - FORM_KEYS:
        abort(400)
    form = _prepare_form()
    if not form.validate_on_submit():
        abort(400)
    action = ACTIONS.get(form.action_key.data)
    if action is None:
        abort(400)
    parameters = dict(LAB_TARGETS[action.key][2])
    if current_app.config.get("AUTOMATION_EXECUTOR") == "mock" and form.simulate.data:
        parameters["simulate"] = form.simulate.data
    try:
        job = queue_and_dispatch(
            server_id=form.server_id.data,
            action_key=action.key,
            parameters=parameters,
            actor=current_user,
        )
    except RemediationUnavailable as exc:
        flash(exc.reason, "warning")
        return redirect(url_for("automation.index"))
    except AutomationRejected:
        abort(400)
    flash(
        job.block_reason or f"Job {job.id} finished with status {job_outcome_label(job)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("automation.detail", job_id=job.id))


@bp.get("/jobs/<int:job_id>")
def detail(job_id):
    job = db.session.get(AutomationJob, job_id)
    if job is None:
        abort(404)
    audits = db.session.scalars(
        select(AuditLog)
        .where(AuditLog.resource_type == "automation_job", AuditLog.resource_id == str(job.id))
        .order_by(AuditLog.created_at.desc())
    ).all()
    retries = db.session.scalars(
        select(AutomationJob).where(AutomationJob.retry_of_job_id == job.id).order_by(AutomationJob.id)
    ).all()
    return render_template("automation/detail.html", job=job, audits=audits, retries=retries)


@bp.post("/jobs/<int:job_id>/retry")
@roles_required("operator", "admin")
def retry(job_id):
    try:
        job = retry_job(job_id, current_user)
    except RemediationUnavailable as exc:
        flash(exc.reason, "warning")
        return redirect(url_for("automation.detail", job_id=job_id))
    except AutomationRejected:
        flash("This job cannot be retried.", "warning")
        return redirect(url_for("automation.detail", job_id=job_id))
    flash(
        job.block_reason or f"Retry job {job.id} finished with status {job_outcome_label(job)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("automation.detail", job_id=job.id))
