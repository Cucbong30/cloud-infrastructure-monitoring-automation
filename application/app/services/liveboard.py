"""Keep lab probes off the request path so the dashboard stays responsive."""

import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models import Alert, Server
from app.services.checklog import observe_hosts
from app.services.checks import management_status
from app.services.inventory import LAB_TARGETS
from app.services.metrics import collect_metrics
from app.services.remediation import consider_live_hosts, schedule_auto_remediation

MAX_AGE_SECONDS = 8
_LOCK = threading.Lock()
_REFRESH = threading.Lock()
_STARTED = False
_STATE = {"metrics": None, "hosts": None, "status": None, "at": 0.0}


def start_live_board(app):
    """One background refresh. Tests keep the synchronous probe path."""
    global _STARTED
    if app.config.get("TESTING"):
        return
    with _LOCK:
        if _STARTED:
            return
        _STARTED = True
    threading.Thread(target=_loop, args=(app,), name="live-board", daemon=True).start()


def load_live_board():
    """Return metrics, hosts, prometheus status, and whether this copy is from the cache."""
    app = current_app._get_current_object()
    if app.config.get("TESTING"):
        metrics, hosts, status = collect_metrics()
        return metrics, hosts, status, False
    start_live_board(app)
    cached = _copy()
    now = time.monotonic()
    if cached is not None and now - cached[3] < MAX_AGE_SECONDS:
        return cached[0], cached[1], cached[2], True
    if cached is not None:
        threading.Thread(target=refresh_once, args=(app,), name="live-board-refresh", daemon=True).start()
        return cached[0], cached[1], cached[2], True
    refresh_once(app, wait=True)
    cached = _copy()
    if cached is not None:
        return cached[0], cached[1], cached[2], True
    metrics, hosts, status = collect_metrics()
    return metrics, hosts, status, False


def refresh_once(app, wait=False):
    if wait:
        acquired = _REFRESH.acquire(timeout=25)
    else:
        acquired = _REFRESH.acquire(blocking=False)
    if not acquired:
        return
    try:
        with app.app_context():
            try:
                metrics, hosts, status = collect_metrics()
                _attach_management(app, hosts)
                observe_hosts(hosts)
                _schedule_auto(hosts)
                _store(metrics, hosts, status)
            except Exception:
                app.logger.exception("Live board refresh failed")
            finally:
                db.session.remove()
    finally:
        _REFRESH.release()


def _loop(app):
    while True:
        started = time.monotonic()
        refresh_once(app)
        time.sleep(max(2.0, MAX_AGE_SECONDS - (time.monotonic() - started)))


def _attach_management(app, hosts):
    names = [host.get("name") for host in hosts if host.get("name")]
    if not names:
        return

    def work(name):
        with app.app_context():
            try:
                server = db.session.scalar(select(Server).where(Server.name == name))
                return name, management_status(server)
            finally:
                db.session.remove()

    with ThreadPoolExecutor(max_workers=min(4, len(names))) as pool:
        found = dict(pool.map(work, names))
    for host in hosts:
        channel = found.get(host.get("name"))
        if channel is not None:
            host["management"] = channel


def _schedule_auto(hosts):
    if not current_app.config.get("AUTO_REMEDIATION_ENABLED"):
        return
    live = consider_live_hosts(hosts)
    lab_names = set(LAB_TARGETS)
    firing = [
        alert
        for alert in db.session.scalars(
            select(Alert).where(Alert.status.in_(("firing", "acknowledged"))).order_by(Alert.starts_at.desc())
        )
        if alert.server and alert.server.name in lab_names
    ]
    merged = []
    seen = set()
    for alert in [*live, *firing]:
        if alert is None or alert.id in seen:
            continue
        seen.add(alert.id)
        merged.append(alert)
    schedule_auto_remediation(merged)


def _store(metrics, hosts, status):
    with _LOCK:
        _STATE["metrics"] = dict(metrics)
        _STATE["hosts"] = copy.deepcopy(hosts)
        _STATE["status"] = status
        _STATE["at"] = time.monotonic()


def _copy():
    with _LOCK:
        if _STATE["hosts"] is None:
            return None
        return (
            dict(_STATE["metrics"]),
            copy.deepcopy(_STATE["hosts"]),
            _STATE["status"],
            _STATE["at"],
        )


def _clear():
    with _LOCK:
        _STATE["metrics"] = None
        _STATE["hosts"] = None
        _STATE["status"] = None
        _STATE["at"] = 0.0
