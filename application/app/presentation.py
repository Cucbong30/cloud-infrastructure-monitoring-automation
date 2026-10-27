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
