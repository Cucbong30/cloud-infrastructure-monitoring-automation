from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template, request
from sqlalchemy import select

from app.authz import roles_required
from app.extensions import db
from app.models import AuditLog

bp = Blueprint("audit", __name__, url_prefix="/audit")
ICT = timezone(timedelta(hours=7))


def _day_bound(text, end=False):
    if not text:
        return None
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return None
    if end:
        parsed = parsed + timedelta(days=1)
    return parsed.replace(tzinfo=ICT).astimezone(timezone.utc)


@bp.get("/")
@roles_required("admin", "operator")
def index():
    date_from = (request.args.get("from") or "").strip()
    date_to = (request.args.get("to") or "").strip()
    action = (request.args.get("action") or "").strip()
    query = select(AuditLog).order_by(AuditLog.created_at.desc())
    start = _day_bound(date_from)
    finish = _day_bound(date_to, end=True)
    if start is not None:
        query = query.where(AuditLog.created_at >= start)
    if finish is not None:
        query = query.where(AuditLog.created_at < finish)
    if action:
        query = query.where(AuditLog.action == action)
    entries = db.session.scalars(query.limit(200)).all()
    return render_template(
        "audit/list.html",
        entries=entries,
        date_from=date_from,
        date_to=date_to,
        action=action,
    )
