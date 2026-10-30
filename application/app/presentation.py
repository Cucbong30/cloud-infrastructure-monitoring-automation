import json
from datetime import datetime, timedelta, timezone

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
    "failed": "danger",
    "Failed": "danger",
    "Blocked": "warning",
    "Verification Failed": "danger",
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
    "remediation": "warning",
    "system": "info",
}


def badge_class(value):
    return BADGE_CLASSES.get(value, "secondary")


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
    kind = getattr(job, "verification_result", None)
    if kind == "blocked":
        return "Blocked"
    if kind == "failed":
        return "Verification Failed"
    output = getattr(job, "output_excerpt", None) or ""
    if "No route to host" in output or "Failed to connect to the host via ssh" in output:
        return "Blocked"
    status = getattr(job, "status", None)
    return job_status_label(status if status is not None else job)


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


def verification_label(job):
    return VERIFICATION_LABELS.get(getattr(job, "verification_result", None))


def verification_summary(job):
    return VERIFICATION_SUMMARIES.get(getattr(job, "verification_result", None))


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
