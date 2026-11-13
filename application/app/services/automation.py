import json
import re

from flask import abort, current_app

from app.executors.ansible import playbook_failure_stage
from app.executors.base import ExecutionResult
from app.extensions import db
from app.executors import EXECUTORS, get_executor
from app.executors.actions import ACTIONS, DENIED_ACTIONS, SERVICE_LABELS
from app.executors.ansible import allowed_parameters
from app.models import AutomationJob, Server, User, utcnow
from app.services.audit import record
from app.services.checks import management_refusal, refuse_unreachable_management, verification_notice, verify_recovery
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
    if action_key in DENIED_ACTIONS:
        raise AutomationRejected(
            "This action is diagnostic only. Auto-remediation does not reboot, clean up disk, delete files, or change the network."
        )
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


def enqueue_job(
    *,
    server_id,
    action_key,
    parameters,
    trigger_source,
    requested_by=None,
    alert_id=None,
    retry_of_job_id=None,
    incident_id=None,
    attempt=None,
):
    action = validate_parameters(action_key, parameters)
    server = db.session.get(Server, server_id) if server_id is not None else None
    if server is None or not server.is_active:
        raise AutomationRejected("Server is not available.")
    if not allowed_parameters(server, action.key, parameters):
        raise AutomationRejected("Action is not allowed for this server.")
    if trigger_source not in {"manual", "remediation", "system", "auto"}:
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
        incident_id=incident_id,
        attempt=attempt,
    )
    _stamp_identity(job, requested_by, trigger_source)
    db.session.add(job)
    db.session.commit()
    record(
        "job.request",
        "automation_job",
        job.id,
        _job_audit(job, server, "QUEUED", "queued", attempt=attempt, incident_id=incident_id),
        user_id=requested_by,
    )
    return job


def _stamp_identity(job, requested_by, trigger_source):
    manual = trigger_source == "manual" or (trigger_source == "remediation" and requested_by)
    if manual:
        user = db.session.get(User, requested_by) if requested_by else None
        email = ((user.email if user is not None else None) or "").strip()
        job.mode = "MANUAL"
        job.triggered_by = email or (user.username if user is not None else "") or "unknown"
        job.user_email = email or None
        job.user_role = None if user is None else user.role
        return
    job.mode = "AUTO"
    job.triggered_by = "SYSTEM"
    job.user_email = None
    job.user_role = "SYSTEM"


def _execution_label(job):
    kind = getattr(job, "verification_result", None)
    if kind in {"passed", "failed"}:
        return "SUCCESS"
    if kind == "blocked":
        return "NOT_RUN"
    if kind == "skipped" and getattr(job, "status", None) == "failed":
        return "FAILED"
    return ""


def _verification_label(job):
    return {"passed": "PASSED", "failed": "FAILED", "blocked": "NOT_RUN", "skipped": "SKIPPED"}.get(
        getattr(job, "verification_result", None),
        "",
    )


def _job_audit(job, server, result, reason, **extra):
    details = {
        "target": None if server is None else server.name,
        "service": SERVICE_LABELS.get(job.action_key, job.action_key),
        "action": job.action_key,
        "action_key": job.action_key,
        "trigger": job.trigger_source,
        "mode": job.mode or ("MANUAL" if job.trigger_source == "manual" else "AUTO"),
        "triggered_by": job.triggered_by or ("SYSTEM" if job.mode != "MANUAL" else None),
        "user_email": job.user_email,
        "user_role": job.user_role,
        "result": result,
        "final_status": job.final_status or result,
        "reason": reason,
        "message": extra.pop("message", reason),
        "alert_id": job.alert_id,
        "incident_id": job.incident_id,
        "job_id": job.id,
        "exit_code": job.exit_code,
        "server_id": job.server_id,
        "execution_result": _execution_label(job),
        "verification_result": _verification_label(job),
    }
    if job.mode == "MANUAL" and job.triggered_by:
        details["actor"] = job.triggered_by
        details["role"] = job.user_role or details.get("role")
    details.update(extra)
    return details


def dispatch(job_id, actor=None):
    job = db.session.get(AutomationJob, job_id)
    if job is None:
        raise AutomationRejected("Job not found.")
    if actor is None:
        if job.trigger_source not in {"remediation", "auto"}:
            raise AutomationRejected("Not allowed.")
    elif getattr(actor, "role", None) not in {"operator", "admin"}:
        abort(403)
    if job.status != "queued":
        raise AutomationRejected("Job is not queued.")

    server = None

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
            _job_audit(job, server, "FAILED", message),
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
        if job.mode == "MANUAL":
            job.final_status = "MANAGEMENT_BLOCKED"
            job.reason = "management_channel_unavailable"
        blocked_result = job.final_status or "BLOCKED"
        db.session.commit()
        record(
            "remediation.blocked",
            "automation_job",
            job.id,
            _job_audit(job, server, blocked_result, refusal["reason"], status="blocked", playbook_executed=False),
            user_id=getattr(actor, "id", None),
        )
        record(
            "job.result",
            "automation_job",
            job.id,
            _job_audit(job, server, blocked_result, refusal["reason"], status="blocked", playbook_executed=False),
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
    execution_result = "FAILED"
    if not result.success:
        stage, task_name = playbook_failure_stage(result.output, getattr(result, "stderr", "") or "")
        job.status = "failed"
        if stage == "verification_failed":
            execution_result = "SUCCESS"
            job.verification_result = "failed"
            job.verification_detail = (
                f"Remediation task succeeded, but verification task '{task_name}' failed."
            )
        else:
            job.verification_result = "skipped"
            job.verification_detail = "Playbook failed before verification."
        audit_action = "remediation.failed"
    else:
        execution_result = "SUCCESS"
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
            audit_action = "remediation.verification_failed"
    if job.verification_result == "failed":
        reason, message = verification_notice(job.action_key)
        job.verification_detail = reason
        audit_action = "remediation.verification_failed"
    else:
        reason, message = None, None
    if not job.final_status:
        if job.verification_result == "passed":
            job.final_status = "SUCCESS"
        elif job.verification_result == "failed":
            job.final_status = "VERIFICATION_FAILED"
        elif job.status == "failed":
            job.final_status = "EXECUTION_FAILED"
    db.session.commit()
    if job.verification_result == "passed":
        outcome = "SUCCESS"
    elif job.verification_result == "failed":
        outcome = "VERIFICATION_FAILED"
    elif job.final_status:
        outcome = job.final_status
    else:
        outcome = "FAILED"
    if job.verification_result == "failed" and execution_result == "SUCCESS":
        record(
            "remediation.execution_succeeded",
            "automation_job",
            job.id,
            _job_audit(
                job,
                server,
                "SUCCESS",
                "remediation execution succeeded",
                message="Remediation execution succeeded. The remediation command completed successfully.",
                execution_result="SUCCESS",
            ),
            user_id=getattr(actor, "id", None),
        )
    record(
        audit_action,
        "automation_job",
        job.id,
        _job_audit(
            job,
            server,
            outcome,
            "verification failed after remediation" if job.verification_result == "failed" else (job.verification_detail or outcome),
            status=job.verification_result,
            detail=job.verification_detail,
            execution_result=execution_result,
            message=message if job.verification_result == "failed" else (job.verification_detail or outcome),
        ),
        user_id=getattr(actor, "id", None),
    )
    record(
        "job.result",
        "automation_job",
        job.id,
        _job_audit(
            job,
            server,
            outcome,
            job.verification_detail or outcome,
            status=job.status,
            execution_result=execution_result,
        ),
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
    server = db.session.get(Server, old.server_id)
    if server is not None:
        reason = refuse_unreachable_management(
            server,
            action_key=old.action_key,
            actor=actor,
            alert_id=old.alert_id,
        )
        if reason:
            raise RemediationUnavailable(reason)
        from app.services.remediation import _action_is_running, _skip_duplicate

        if _action_is_running(server.id, old.action_key):
            user = db.session.get(User, getattr(actor, "id", None)) if getattr(actor, "id", None) else None
            email = ((user.email if user is not None else None) or "").strip()
            triggered_by = email or (user.username if user is not None else "") or "unknown"
            return _skip_duplicate(server, old.action_key, user, triggered_by, None if user is None else user.role)
    job = enqueue_job(
        server_id=old.server_id,
        action_key=old.action_key,
        parameters=parameters,
        trigger_source="manual",
        requested_by=getattr(actor, "id", None),
        alert_id=old.alert_id,
        retry_of_job_id=old.id,
    )
    record(
        "remediation.retry",
        "automation_job",
        job.id,
        _job_audit(
            job,
            server,
            "RETRY",
            "retry",
            message=f"Manual retry of job {old.id} for {old.action_key}.",
            final_status="RETRY",
            retry_of_job_id=old.id,
        ),
        user_id=getattr(actor, "id", None),
    )
    return dispatch(job.id, actor=actor)
