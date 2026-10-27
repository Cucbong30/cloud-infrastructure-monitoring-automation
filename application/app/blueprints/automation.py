from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import select

from app.authz import roles_required
from app.executors.actions import ACTIONS, LAB_TARGETS
from app.extensions import db
from app.forms import JobForm
from app.models import AutomationJob, Server
from app.presentation import job_status_label
from app.services.automation import REJECTED_PARAMETER_KEYS, AutomationRejected, queue_and_dispatch
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
    for server in db.session.scalars(select(Server).where(Server.is_active.is_(True)).order_by(Server.name)):
        reason = blocked_reason(server)
        if reason and (server.name or "").upper() in LAB_ACTIONS:
            notices.append(reason)
    return render_template("automation/list.html", jobs=jobs, form=form, actions=ACTIONS, unreachable_notices=notices)


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
    server = db.session.get(Server, form.server_id.data)
    reason = blocked_reason(server)
    if reason:
        flash(reason, "warning")
        return redirect(url_for("automation.index"))
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
    except AutomationRejected:
        abort(400)
    flash(
        f"Job {job.id} finished with status {job_status_label(job.status)}.",
        "success" if job.status == "succeeded" else "warning",
    )
    return redirect(url_for("automation.index"))
