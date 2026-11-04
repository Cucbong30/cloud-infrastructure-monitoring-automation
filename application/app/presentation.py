import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

BADGE_CLASSES = {
    "online": "success",
    "warning": "warning",
    "down": "danger",
    "maintenance": "secondary",
    "unknown": "light",
    "N/A": "secondary",
    "Online": "success",
    "Healthy": "success",
    "Degraded": "warning",
    "Unreachable": "danger",
    "UP": "success",
    "DOWN": "danger",
    "firing": "danger",
    "acknowledged": "warning",
    "resolved": "success",
    "critical": "danger",
    "info": "info",
    "queued": "secondary",
    "Pending": "secondary",
    "running": "primary",
    "Running": "primary",
    "succeeded": "success",
    "Success": "success",
    "SUCCESS": "success",
    "failed": "danger",
    "Failed": "danger",
    "FAILED": "danger",
    "EXECUTION_FAILED": "danger",
    "COOLDOWN_SKIPPED": "secondary",
    "DUPLICATE_SKIPPED": "secondary",
    "Blocked": "warning",
    "BLOCKED": "warning",
    "Verification Failed": "danger",
    "VERIFICATION_FAILED": "danger",
    "MANUAL_REQUIRED": "warning",
    "PENDING": "secondary",
    "RUNNING": "primary",
    "CANCELED": "dark",
    "canceled": "dark",
    "admin": "danger",
    "operator": "primary",
    "viewer": "secondary",
    "linux": "dark",
    "windows": "info",
    "mock": "secondary",
    "ansible": "dark",
    "powershell": "primary",
    "shell": "dark",
    "manual": "secondary",
    "Manual": "secondary",
    "remediation": "warning",
    "auto": "primary",
    "Auto": "primary",
    "system": "info",
    "System": "info",
}


def badge_class(value):
    return BADGE_CLASSES.get(value, "secondary")


def trigger_label(job):
    source = getattr(job, "trigger_source", None)
    if source == "auto":
        return "Auto"
    if source == "manual":
        return "Manual"
    if source == "system":
        return "System"
    if source == "remediation":
        return "Manual" if getattr(job, "requested_by", None) else "Auto"
    return source or "—"


JOB_STATUS_LABELS = {
    "queued": "Pending",
    "running": "Running",
    "succeeded": "Success",
    "failed": "Failed",
    "canceled": "Canceled",
}


def job_status_label(status):
    return JOB_STATUS_LABELS.get(status, status or "—")


def job_outcome_label(job):
    """Final status shown on Job Detail and the job list."""
    stored = getattr(job, "final_status", None)
    if stored:
        return stored
    kind = getattr(job, "verification_result", None)
    output = getattr(job, "output_excerpt", None) or ""
    if kind == "blocked" or "No route to host" in output or "Failed to connect to the host via ssh" in output:
        return "BLOCKED"
    if kind == "failed":
        return "VERIFICATION_FAILED"
    status = getattr(job, "status", None)
    if status is None:
        return job_status_label(job)
    if status == "succeeded":
        return "SUCCESS"
    if status == "failed":
        if getattr(job, "reason", None) == "retry_limit" or (kind == "skipped" and _retry_ended_manual(job)):
            return "MANUAL_REQUIRED"
        return "EXECUTION_FAILED"
    return {"queued": "PENDING", "running": "RUNNING", "canceled": "CANCELED"}.get(status, job_status_label(status))


def _retry_ended_manual(job):
    if getattr(job, "retry_of_job_id", None):
        return True
    job_id = getattr(job, "id", None)
    if not job_id:
        return False
    try:
        from flask import has_app_context

        from app.extensions import db
        from app.models import AutomationJob
    except Exception:
        return False
    if not has_app_context():
        return False
    later = db.session.scalar(
        select(AutomationJob.id).where(
            AutomationJob.retry_of_job_id == job_id,
            AutomationJob.status == "failed",
            AutomationJob.verification_result == "skipped",
        )
    )
    return later is not None


VERIFICATION_LABELS = {
    "passed": "Passed",
    "failed": "Verification failed",
    "blocked": "Blocked",
    "skipped": "Skipped",
}

VERIFICATION_SUMMARIES = {
    "passed": "The service responded after the action.",
    "failed": "The action finished, but the service was still down.",
    "blocked": "The management channel was down, so the playbook did not run.",
    "skipped": "The playbook failed before verification.",
}


def execution_result_label(job):
    """The remediation command, separate from the post-check."""
    kind = getattr(job, "verification_result", None)
    if kind in {"passed", "failed"}:
        return "SUCCESS"
    if kind == "blocked":
        return "NOT_RUN"
    if kind == "skipped" and getattr(job, "status", None) == "failed":
        return "FAILED"
    return "—"


def verification_label(job):
    return VERIFICATION_LABELS.get(getattr(job, "verification_result", None))


def verification_summary(job):
    return VERIFICATION_SUMMARIES.get(getattr(job, "verification_result", None))


def audit_facts(entry):
    """Target, action, trigger, result, and reason stored on an audit row."""
    raw = getattr(entry, "details_json", None) or ""
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    reason = data.get("message") or data.get("reason") or "—"
    return {
        "target": data.get("target") or "—",
        "action": data.get("action") or data.get("action_key") or getattr(entry, "action", "—"),
        "trigger": data.get("trigger") or data.get("trigger_source") or "—",
        "result": data.get("result") or "—",
        "reason": reason,
    }


def audit_message(entry):
    raw = getattr(entry, "details_json", None) or ""
    try:
        data = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return raw or "—"
    if isinstance(data, dict) and data.get("message"):
        return data["message"]
    return raw or "—"


def format_clock(value):
    """Clock shown in the tables and event log, minute precision."""
    if not value:
        return "now"
    parsed = value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return value
    if getattr(parsed, "tzinfo", None) is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")


def job_duration_seconds(job):
    start = getattr(job, "started_at", None)
    end = getattr(job, "finished_at", None)
    if start is None or end is None:
        return None
    if start.tzinfo is None and end.tzinfo is not None:
        start = start.replace(tzinfo=end.tzinfo)
    if end.tzinfo is None and start.tzinfo is not None:
        end = end.replace(tzinfo=start.tzinfo)
    seconds = (end - start).total_seconds()
    if seconds < 0:
        return None
    return int(seconds)
