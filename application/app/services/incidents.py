"""Incident lifecycle.

open -> acknowledged is a person accepting the outage.
open -> in_progress is allowed for auto-remediation without that acknowledgement.
in_progress returns to open or acknowledged when no job is still running.
resolved means the service check passed. closed is allowed only after that.
A resolved or closed incident stays in history. The next outage is a new row.
"""

from app.extensions import db
from app.models import IncidentEvent, utcnow

ACTIVE_STATUSES = ("open", "acknowledged", "in_progress")
TERMINAL_STATUSES = ("resolved", "closed")

ALLOWED = {
    "open": {"acknowledged", "in_progress", "resolved"},
    "acknowledged": {"in_progress", "resolved"},
    "in_progress": {"open", "acknowledged", "resolved"},
    "resolved": {"closed"},
    "closed": set(),
}


class IncidentTransitionError(ValueError):
    """The requested status is not a legal next step."""


def add_event(
    incident,
    event_key,
    message,
    *,
    to_status=None,
    actor=None,
    job_id=None,
    approval_id=None,
):
    """Record who changed the incident. Raise when the status step is illegal."""
    if incident is None:
        return None
    previous = incident.status
    destination = previous if to_status is None else to_status
    if destination != previous and destination not in ALLOWED.get(previous, ()):
        raise IncidentTransitionError(
            f"Cannot move incident {incident.id} from {previous} to {destination}."
        )
    if destination != previous:
        _stamp(incident, destination, actor)
        incident.status = destination
    event = IncidentEvent(
        incident_id=incident.id,
        from_status=previous,
        to_status=destination,
        event_key=event_key[:40],
        message=(message or "")[:255],
        actor_id=getattr(actor, "id", None),
        actor_name=_actor_name(actor),
        actor_role=_actor_role(actor),
        job_id=job_id,
        approval_id=approval_id,
        created_at=utcnow(),
    )
    db.session.add(event)
    return event


def acknowledge(incident, actor):
    if incident is None:
        raise IncidentTransitionError("Incident was not found.")
    if incident.status != "open":
        raise IncidentTransitionError("Only an open incident can be acknowledged.")
    add_event(
        incident,
        "acknowledged",
        "Incident accepted.",
        to_status="acknowledged",
        actor=actor,
    )


def close(incident, actor, reason=""):
    if incident is None:
        raise IncidentTransitionError("Incident was not found.")
    if incident.status == "closed":
        raise IncidentTransitionError("This incident is already closed.")
    if incident.status != "resolved":
        raise IncidentTransitionError("Only a resolved incident can be closed.")
    text = (reason or "Incident confirmed complete.").strip()
    add_event(incident, "closed", text, to_status="closed", actor=actor)
    incident.reason = (incident.reason or "closed")[:80]


def enter_progress(incident, message, *, actor=None, job_id=None, approval_id=None, retry=False):
    """Move an open or acknowledged incident into remediation. A retry stays in progress."""
    if incident is None or incident.status in TERMINAL_STATUSES:
        return None
    destination = None if incident.status == "in_progress" else "in_progress"
    key = "retry" if retry else "remediation_started"
    return add_event(
        incident,
        key,
        message,
        to_status=destination,
        actor=actor,
        job_id=job_id,
        approval_id=approval_id,
    )


def note_approval(incident, event_key, message, *, actor=None, approval_id=None, job_id=None):
    """Record an approval step. A rejected or expired request leaves the waiting state."""
    if incident is None:
        return None
    destination = None
    if event_key in {"approval_rejected", "approval_expired"} and incident.status == "in_progress":
        destination = _waiting_status(incident)
    return add_event(
        incident,
        event_key,
        message,
        to_status=destination,
        actor=actor,
        approval_id=approval_id,
        job_id=job_id,
    )


def note_result(incident, event_key, message, *, job_id=None, approval_id=None):
    """Keep a failed or blocked job on the timeline without marking the incident resolved."""
    if incident is None or incident.status in TERMINAL_STATUSES:
        return None
    return add_event(
        incident,
        event_key,
        message,
        job_id=job_id,
        approval_id=approval_id,
    )


def release_work(incident, event_key, message, *, job_id=None, approval_id=None, actor=None):
    """Leave in_progress once the job has stopped. The incident stays unresolved."""
    if incident is None or incident.status in TERMINAL_STATUSES:
        return None
    destination = _waiting_status(incident) if incident.status == "in_progress" else None
    return add_event(
        incident,
        event_key,
        message,
        to_status=destination,
        actor=actor,
        job_id=job_id,
        approval_id=approval_id,
    )


def _waiting_status(incident):
    if incident.acknowledged_at:
        return "acknowledged"
    return "open"


def _stamp(incident, status, actor):
    now = utcnow()
    user_id = getattr(actor, "id", None)
    if status == "acknowledged":
        incident.acknowledged_at = now
        incident.acknowledged_by = user_id
    elif status == "in_progress":
        if incident.progress_at is None:
            incident.progress_at = now
            incident.progress_by = user_id
    elif status == "resolved":
        incident.resolved_at = now
        incident.closed_at = now
    elif status == "closed":
        incident.closed_at = now
        incident.closed_by = user_id


def _actor_name(actor):
    if actor is None:
        return "SYSTEM"
    email = (getattr(actor, "email", None) or "").strip()
    return email or getattr(actor, "username", None) or "SYSTEM"


def _actor_role(actor):
    if actor is None:
        return "SYSTEM"
    return getattr(actor, "role", None) or "SYSTEM"
