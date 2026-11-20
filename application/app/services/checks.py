import time

from flask import current_app, g

from app.services.probes import http_probe, tcp_probe

MANAGEMENT_CHANNELS = {
    "WEB01": {"label": "SSH", "host": "192.168.10.11", "port": 22},
    "APP01": {"label": "SSH", "host": "192.168.10.12", "port": 22},
    "WIN01": {"label": "WinRM", "host": "192.168.10.13", "port": 5985},
}

ACTION_CHANNELS = {
    "restart_nginx": "WEB01",
    "restart_container": "APP01",
    "restart_windows_exporter": "WIN01",
}


def management_channels():
    channels = dict(MANAGEMENT_CHANNELS)
    from app.services.inventory import azure_settings

    settings = azure_settings()
    channels["AZURE01"] = {
        "label": "SSH",
        "host": settings["ip"] if settings["configured"] else "",
        "port": 22,
        "configured": settings["configured"],
    }
    return channels


def _refusal(name, status):
    reason = f"{name} management channel {status['label']} :{status['port']} is down"
    message = f"Remediation unavailable. {reason}."
    return message, reason

SERVICE_CHECKS = {
    "restart_nginx": ("http", "http://192.168.10.11/", "Nginx :80"),
    "restart_container": ("http", "http://192.168.10.12:8080/", "App :8080"),
    "restart_windows_exporter": ("http", "http://192.168.10.13:9182/metrics", "Windows Exporter :9182"),
}


def verification_notice(action_key):
    """Human wording for a successful command whose post-check failed."""
    spec = SERVICE_CHECKS.get(action_key)
    port = None
    if spec and ":" in spec[2]:
        tail = spec[2].rsplit(":", 1)[-1].strip()
        if tail.isdigit():
            port = tail
    where = f" on port {port}" if port else ""
    reason = f"The remediation command completed successfully, but the post-check{where} failed."
    message = (
        "Remediation completed, but verification failed. "
        f"{reason} No retry was performed. Manual intervention is required."
    )
    return reason, message


def _management_probe():
    """Ansible reaches targets from MON01, so the gate uses that path."""
    try:
        ansible = current_app.config.get("AUTOMATION_EXECUTOR") == "ansible"
    except RuntimeError:
        ansible = False
    if not ansible:
        return tcp_probe
    from app.executors.ansible import controller_port_open

    return controller_port_open


def probe_management(name, probe_tcp=None, timeout=2):
    spec = management_channels().get((name or "").upper())
    if spec is None:
        return None
    if spec.get("configured") is False or not spec.get("host"):
        return {
            "label": spec["label"],
            "status": "DOWN",
            "text": f"{spec['label']} not configured",
            "host": spec.get("host") or "",
            "port": spec["port"],
            "latency_ms": None,
        }
    probe = _management_probe() if probe_tcp is None else probe_tcp
    result = probe(spec["host"], spec["port"], timeout=timeout)
    if isinstance(result, tuple):
        ok = bool(result[0]) if result else False
        latency = result[1] if len(result) > 1 else None
    else:
        ok, latency = bool(result), None
    state = "UP" if ok else "DOWN"
    return {
        "label": spec["label"],
        "status": state,
        "text": f"{spec['label']} {state}",
        "host": spec["host"],
        "port": spec["port"],
        "latency_ms": latency,
    }


def management_status(server):
    """Live management channel for a server. Host health does not use this result."""
    if server is None:
        return None
    override = current_app.config.get("MANAGEMENT_STATUS")
    if override is not None:
        return override(server)
    name = (getattr(server, "name", None) or "").upper()
    if name not in management_channels():
        return None
    if current_app.config.get("AUTOMATION_EXECUTOR") != "ansible":
        return None
    cache = getattr(g, "management_status_cache", None)
    if cache is None:
        cache = {}
        g.management_status_cache = cache
    key = getattr(server, "id", None) or name
    if key not in cache:
        timeout = float(current_app.config.get("PROBE_TIMEOUT_SECONDS", 2))
        cache[key] = probe_management(name, timeout=timeout)
    return cache[key]


def channel_name(server, action_key=None):
    server_name = (getattr(server, "name", None) or "").upper()
    if server_name in management_channels():
        return server_name
    if action_key in ACTION_CHANNELS:
        return ACTION_CHANNELS[action_key]
    return server_name


def channel_probe(server, action_key=None):
    """Probe the management port for this action. restart_container always checks APP01 SSH :22."""
    if current_app.config.get("MANAGEMENT_STATUS") is not None and action_key not in ACTION_CHANNELS:
        return management_status(server)
    name = channel_name(server, action_key)
    if name not in management_channels():
        return None
    if current_app.config.get("AUTOMATION_EXECUTOR") != "ansible":
        return None
    if (
        current_app.config.get("MANAGEMENT_STATUS") is not None
        and server is not None
        and (getattr(server, "name", None) or "").upper() == name
    ):
        return management_status(server)
    timeout = float(current_app.config.get("PROBE_TIMEOUT_SECONDS", 2))
    return probe_management(name, timeout=timeout)


def management_refusal(server, action_key=None):
    """Return message and reason when the management channel is down, else None."""
    checker = current_app.config.get("MANAGEMENT_CHECK")
    if checker is not None:
        text = checker(server)
        if not text:
            return None
        return {"message": text, "reason": text, "status": None}
    status = channel_probe(server, action_key)
    if not status or status.get("status") != "DOWN":
        return None
    message, reason = _refusal(channel_name(server, action_key), status)
    return {"message": message, "reason": reason, "status": status}


def management_block(server, action_key=None):
    """Return the text shown when SSH or WinRM is down, else None."""
    refusal = management_refusal(server, action_key)
    if refusal is None:
        return None
    return refusal["message"]


def refuse_unreachable_management(server, *, action_key, actor=None, alert_id=None):
    """Audit and return the refusal message. No remediation job is created."""
    refusal = management_refusal(server, action_key)
    if refusal is None:
        return None
    from app.services.audit import record

    status = refusal.get("status")
    record(
        "remediation.blocked",
        "server",
        getattr(server, "id", None),
        {
            "reason": refusal["reason"],
            "message": refusal["message"],
            "action_key": action_key,
            "alert_id": alert_id,
            "server_id": getattr(server, "id", None),
            "channel": None if status is None else status.get("text"),
            "host": None if status is None else status.get("host"),
            "port": None if status is None else status.get("port"),
        },
        user_id=getattr(actor, "id", None),
    )
    return management_block(server)


def service_probe(server, action_key):
    name = (getattr(server, "name", None) or "").upper()
    if name == "AZURE01" and action_key == "restart_nginx":
        from app.services.inventory import azure_settings

        settings = azure_settings()
        if not settings["nginx_url"]:
            return None
        return ("http", settings["nginx_url"], "Nginx :80")
    return SERVICE_CHECKS.get(action_key)


def verify_recovery(server, action_key):
    """Return (ok, detail). Success requires this post-check, not only exit code 0."""
    checker = current_app.config.get("RECOVERY_CHECK")
    if checker is not None:
        return checker(server, action_key)
    if current_app.config.get("AUTOMATION_EXECUTOR") != "ansible":
        return True, "Mock post-check passed."
    spec = service_probe(server, action_key)
    if spec is None:
        return False, "No post-check is defined for this action."
    kind, target, label = spec
    detail = f"{label} did not respond."
    for attempt in range(3):
        if kind == "http":
            ok, latency = http_probe(target, timeout=3)
        else:
            host, port = target
            ok, latency = tcp_probe(host, port, timeout=3)
        if ok:
            return True, f"{label} is up ({latency} ms)."
        detail = f"{label} did not respond."
        if attempt < 2:
            time.sleep(1)
    return False, detail
