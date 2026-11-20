import os

from sqlalchemy import select

from app.models import Server

LAB_TARGETS = {
    "WEB01": {
        "hostname": "WEB01",
        "ip_address": "192.168.10.11",
        "os_type": "linux",
        "monitoring_target": "192.168.10.11:9100",
        "environment": "local",
        "provider": "vmware",
        "automation_group": "linux_web",
    },
    "APP01": {
        "hostname": "APP01",
        "ip_address": "192.168.10.12",
        "os_type": "linux",
        "monitoring_target": "192.168.10.12:9100",
        "environment": "local",
        "provider": "vmware",
        "automation_group": "linux_app",
    },
    "WIN01": {
        "hostname": "WIN01",
        "ip_address": "192.168.10.13",
        "os_type": "windows",
        "monitoring_target": "192.168.10.13:9182",
        "environment": "local",
        "provider": "vmware",
        "automation_group": "windows_app",
    },
    "MON01": {
        "hostname": "MON01",
        "ip_address": "192.168.10.10",
        "os_type": "linux",
        "monitoring_target": "192.168.10.10:9100",
        "environment": "local",
        "provider": "vmware",
        "automation_group": "linux_mon",
    },
    "AZURE01": {
        "hostname": "AZURE01",
        "ip_address": "0.0.0.0",
        "os_type": "linux",
        "monitoring_target": "AZURE01:9100",
        "environment": "cloud",
        "provider": "azure",
        "automation_group": "azure_linux",
    },
}

INSTANCE_ALIASES = {
    "192.168.10.11:9100": "WEB01",
    "192.168.10.11": "WEB01",
    "web01": "WEB01",
    "192.168.10.12:9100": "APP01",
    "192.168.10.12": "APP01",
    "app01": "APP01",
    "192.168.10.13:9182": "WIN01",
    "192.168.10.13": "WIN01",
    "win01": "WIN01",
    "192.168.10.10:9100": "MON01",
    "localhost:9090": "MON01",
    "127.0.0.1:9090": "MON01",
    "192.168.10.10:9090": "MON01",
    "192.168.10.10": "MON01",
    "mon01": "MON01",
    "azure01": "AZURE01",
    "AZURE01": "AZURE01",
    "AZURE01:9100": "AZURE01",
}


def _setting(name, default=""):
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            value = current_app.config.get(name)
            if value is not None and str(value).strip() != "":
                return str(value).strip()
    except RuntimeError:
        pass
    return (os.environ.get(name) or default).strip()


def azure_settings():
    """Cloud target address. Empty until AZURE01_IP is set, so the portal does not probe a guessed host."""
    ip = _setting("AZURE01_IP")
    exporter = _setting("AZURE01_EXPORTER") or (f"{ip}:9100" if ip else "AZURE01:9100")
    nginx = _setting("AZURE01_NGINX_URL") or (f"http://{ip}/" if ip else "")
    playbook = _setting("AZURE01_PLAYBOOK", "~/ansible/playbooks/restart-azure-nginx.yml")
    return {
        "ip": ip or "0.0.0.0",
        "configured": bool(ip),
        "exporter": exporter,
        "nginx_url": nginx,
        "playbook": playbook,
    }


def refresh_cloud_target():
    settings = azure_settings()
    LAB_TARGETS["AZURE01"] = {
        "hostname": "AZURE01",
        "ip_address": settings["ip"],
        "os_type": "linux",
        "monitoring_target": settings["exporter"],
        "environment": "cloud",
        "provider": "azure",
        "automation_group": "azure_linux",
    }
    for key in (settings["ip"], settings["exporter"], "azure01", "AZURE01"):
        if key and key != "0.0.0.0":
            INSTANCE_ALIASES[key] = "AZURE01"
    INSTANCE_ALIASES["azure01"] = "AZURE01"
    INSTANCE_ALIASES["AZURE01"] = "AZURE01"
    INSTANCE_ALIASES["AZURE01:9100"] = "AZURE01"
    from app.services.metrics import HOST_CHECKS

    HOST_CHECKS["AZURE01"] = {
        "role": "Cloud Web Server",
        "exporter_label": "Node Exporter :9100",
        "exporter_short": "E",
        "services": [
            {"name": "Nginx :80", "short": "N", "kind": "http", "url": settings["nginx_url"]},
        ],
    }
    return settings


def instance_candidates(*values):
    found = []
    for value in values:
        if not value:
            continue
        text = str(value).strip()
        if not text or text in found:
            continue
        found.append(text)
        if ":" in text:
            host = text.split(":", 1)[0]
            if host not in found:
                found.append(host)
    return found


def canonical_server_name(instance):
    if not instance:
        return None
    key = str(instance).strip()
    if key in INSTANCE_ALIASES:
        return INSTANCE_ALIASES[key]
    host = key.split(":", 1)[0]
    return INSTANCE_ALIASES.get(host) or INSTANCE_ALIASES.get(host.lower())


def match_server(*values, labels=None):
    refresh_cloud_target()
    candidates = list(instance_candidates(*values))
    if labels:
        for key in ("instance", "monitoring_target", "hostname", "host", "ip", "job"):
            raw = labels.get(key)
            if raw:
                candidates.extend(instance_candidates(raw))
    seen = []
    for candidate in candidates:
        if candidate not in seen:
            seen.append(candidate)
    servers = list(db_servers())
    by_target = {server.monitoring_target: server for server in servers if server.monitoring_target}
    by_name = {server.name: server for server in servers}
    by_host = {server.hostname: server for server in servers}
    by_ip = {server.ip_address: server for server in servers}
    for candidate in seen:
        mapped = canonical_server_name(candidate)
        if mapped and mapped in by_name:
            return by_name[mapped]
        if candidate in by_target:
            return by_target[candidate]
        if candidate in by_name:
            return by_name[candidate]
        if candidate in by_host:
            return by_host[candidate]
        if candidate in by_ip:
            return by_ip[candidate]
    return None


def db_servers():
    from app.extensions import db

    return list(db.session.scalars(select(Server)))
