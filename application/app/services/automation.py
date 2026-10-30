import json
import re

from flask import abort, current_app

from app.executors.base import ExecutionResult
from app.extensions import db
from app.executors import EXECUTORS, get_executor
from app.executors.actions import ACTIONS
from app.executors.ansible import allowed_parameters
from app.models import AutomationJob, Server, utcnow
from app.services.audit import record
from app.services.checks import management_refusal, refuse_unreachable_management, verify_recovery
from app.validation import TOKEN_RE

REJECTED_PARAMETER_KEYS = {"command", "cmd", "playbook", "script", "shell", "playbook_path"}
SECRET_LINE = re.compile(r"(password|passwd|token|secret|authorization|api[_-]?key)\s*[:=]", re.IGNORECASE)


class AutomationRejected(ValueError):
    pass


class RemediationUnavailable(Exception):
    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def validate_parameters(action_key, parameters):
    if not isinstance(parameters, dict):
        raise AutomationRejected("Invalid parameters.")
    if action_key not in ACTIONS:
        raise AutomationRejected("Action is not allowed.")
    if REJECTED_PARAMETER_KEYS & set(parameters):
        raise AutomationRejected("Parameter is not allowed.")
    action = ACTIONS[action_key]
    allowed = set(action.params) | {"simulate"}
    if action.dry_run:
        allowed.add("dry_run")
    if set(parameters) - allowed:
        raise AutomationRejected("Parameter is not allowed.")
    for value in parameters.values():
        if not isinstance(value, str) or not TOKEN_RE.match(value):
            raise AutomationRejected("Invalid parameter value.")
    if "simulate" in parameters and parameters["simulate"] not in {"fail", "success"}:
        raise AutomationRejected("Invalid parameter value.")
    for key in action.params:
        if not parameters.get(key):
            raise AutomationRejected("Missing parameter.")
    if action.dry_run:
        parameters["dry_run"] = "true"
    return action


def scrub_output(output, limit):
    lines = []
    for line in (output or "").splitlines():
        if SECRET_LINE.search(line) or "bearer " in line.lower():
            lines.append("[redacted]")
        else:
            lines.append(line)
    text = "\n".join(lines)
    if len(text) > limit:
        return text[:limit] + "\n[truncated]"
    return text


def enqueue_job(*, server_id, action_key, parameters, trigger_source, requested_by=None, alert_id=None, retry_of_job_id=None):
    action = validate_parameters(action_key, parameters)
    server = db.session.get(Server, server_id) if server_id is not None else None
    if server is None or not server.is_active:
        raise AutomationRejected("Server is not available.")
    if not allowed_parameters(server, action.key, parameters):
        raise AutomationRejected("Action is not allowed for this server.")
    if trigger_source not in {"manual", "remediation", "system"}:
        raise AutomationRejected("Invalid trigger.")
    executor_name = current_app.config.get("AUTOMATION_EXECUTOR", "mock")
    if executor_name not in EXECUTORS:
        raise AutomationRejected("Unknown executor.")
    job = AutomationJob(
        server_id=server.id,
        alert_id=alert_id,
        requested_by=requested_by,
        trigger_source=trigger_source,
        executor=executor_name,
        action_key=action.key,
        parameters_json=json.dumps(parameters, sort_keys=True),
        status="queued",
        created_at=utcnow(),
        retry_of_job_id=retry_of_job_id,
    )
    db.session.add(job)
    db.session.commit()
    record(
        "job.request",
        "automation_job",
        job.id,
        {
            "action_key": action.key,
            "trigger_source": trigger_source,
            "alert_id": alert_id,
            "server_id": server.id,
        },
        user_id=requested_by,
    )
    return job


def dispatch(job_id, actor=None):
    job = db.session.get(AutomationJob, job_id)
    if job is None:
        raise AutomationRejected("Job not found.")
    if actor is None:
        if job.trigger_source != "remediation":
            raise AutomationRejected("Not allowed.")
    elif getattr(actor, "role", None) not in {"operator", "admin"}:
        abort(403)
    if job.status != "queued":
        raise AutomationRejected("Job is not queued.")

    def _fail(message):
        now = utcnow()
        job.status = "failed"
        job.exit_code = 1
        job.output_excerpt = scrub_output(message, current_app.config["JOB_OUTPUT_MAX_CHARS"])
        job.started_at = job.started_at or now
        job.finished_at = now
        db.session.commit()
        record(
            "job.result",
            "automation_job",
            job.id,
            {"status": job.status, "exit_code": job.exit_code, "alert_id": job.alert_id},
            user_id=getattr(actor, "id", None),
        )
        return job

    server = db.session.get(Server, job.server_id) if job.server_id else None
    if server is None or not server.is_active:
        return _fail("Server is not available.")
    refusal = management_refusal(server, job.action_key)
    if refusal:
        now = utcnow()
        job.status = "failed"
        job.block_reason = refusal["reason"]
        job.verification_result = "blocked"
        job.verification_detail = refusal["message"]
        job.started_at = now
        job.finished_at = now
        db.session.commit()
        record(
            "remediation.blocked",
            "automation_job",
            job.id,
            {
                "action_key": job.action_key,
                "alert_id": job.alert_id,
                "server_id": job.server_id,
                "reason": refusal["reason"],
            },
            user_id=getattr(actor, "id", None),
        )
        record(
            "job.result",
            "automation_job",
            job.id,
            {"status": "blocked", "exit_code": None, "alert_id": job.alert_id},
            user_id=getattr(actor, "id", None),
        )
        return job
    try:
        parameters = json.loads(job.parameters_json or "{}")
        action = validate_parameters(job.action_key, parameters)
    except (AutomationRejected, json.JSONDecodeError):
        return _fail("Action is not allowed.")
    if job.executor not in EXECUTORS:
        return _fail("Real execution is disabled in MVP.")

    job.parameters_json = json.dumps(parameters, sort_keys=True)
    job.status = "running"
    job.started_at = utcnow()
    db.session.commit()

    try:
        result = get_executor(job.executor)().execute(job, server, action)
    except Exception:
        current_app.logger.exception("automation executor failed")
        now = utcnow()
        result = ExecutionResult(False, 1, "Executor failed without a result.", now, now)
    limit = current_app.config["JOB_OUTPUT_MAX_CHARS"]
    job.exit_code = result.exit_code
    job.output_excerpt = scrub_output(result.output, limit)
    job.stderr_excerpt = scrub_output(getattr(result, "stderr", "") or "", limit)
    job.finished_at = result.finished_at or utcnow()
    if not result.success:
        job.status = "failed"
        job.verification_result = "skipped"
        job.verification_detail = "Playbook failed before verification."
        audit_action = "remediation.failed"
    else:
        try:
            verified, detail = verify_recovery(server, job.action_key)
        except Exception:
            current_app.logger.exception("recovery verification failed")
            verified, detail = False, "Post-check failed before a result was returned."
        job.verification_detail = detail
        if verified:
            job.status = "succeeded"
            job.verification_result = "passed"
            audit_action = "remediation.verified"
        else:
            job.status = "failed"
            job.verification_result = "failed"
            audit_action = "remediation.failed"
    db.session.commit()
    record(
        audit_action,
        "automation_job",
        job.id,
        {
            "status": job.verification_result,
            "exit_code": job.exit_code,
            "alert_id": job.alert_id,
            "detail": job.verification_detail,
        },
        user_id=getattr(actor, "id", None),
    )
    record(
        "job.result",
        "automation_job",
        job.id,
        {"status": job.status, "exit_code": job.exit_code, "alert_id": job.alert_id},
        user_id=getattr(actor, "id", None),
    )
    return job


def queue_and_dispatch(
    *,
    server_id,
    action_key,
    parameters,
    actor,
    alert_id=None,
    trigger_source="manual",
    retry_of_job_id=None,
):
    server = db.session.get(Server, server_id)
    if server is not None:
        reason = refuse_unreachable_management(
            server,
            action_key=action_key,
            actor=actor,
            alert_id=alert_id,
        )
        if reason:
            raise RemediationUnavailable(reason)
    job = enqueue_job(
        server_id=server_id,
        action_key=action_key,
        parameters=parameters,
        trigger_source=trigger_source,
        requested_by=getattr(actor, "id", None),
        alert_id=alert_id,
        retry_of_job_id=retry_of_job_id,
    )
    return dispatch(job.id, actor=actor)


def retry_job(job_id, actor):
    old = db.session.get(AutomationJob, job_id)
    if old is None:
        raise AutomationRejected("Job not found.")
    if old.status != "failed":
        raise AutomationRejected("Only a failed job can be retried.")
    parameters = json.loads(old.parameters_json or "{}")
    return queue_and_dispatch(
        server_id=old.server_id,
        action_key=old.action_key,
        parameters=parameters,
        actor=actor,
        alert_id=old.alert_id,
        trigger_source=old.trigger_source,
        retry_of_job_id=old.id,
    )
