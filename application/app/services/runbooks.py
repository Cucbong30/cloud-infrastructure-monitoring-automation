"""One registry for action runbooks, risk, and the alert that selects each action."""
import re

RUNBOOKS = {
    "nginx-verification-failed": {
        "title": "Nginx verification failed",
        "applies": "WEB01 and AZURE01 after restart_nginx",
        "summary": "The restart command finished, but HTTP on port 80 did not return 200. Do not retry automatically.",
        "steps": (
            "Confirm the playbook task Restart nginx service is changed or ok.",
            "On the target, run nginx -t and read the journal for nginx.",
            "Check whether nginx is listening on port 80, not only on another port.",
            "Restore a valid site config, then start nginx and request http://<target>/.",
        ),
    },
    "nginx-execution-failed": {
        "title": "Nginx execution failed",
        "applies": "WEB01 and AZURE01 when systemctl restart nginx fails",
        "summary": "The remediation command failed. Auto policy retries once. A manual run does not retry by itself.",
        "steps": (
            "Read the job stderr for the nginx or sudo error.",
            "Fix the unit or the config that made systemctl restart nginx fail.",
            "Run the action again from the portal only after the config test passes.",
        ),
    },
    "nginx-management-blocked": {
        "title": "Nginx management channel blocked",
        "applies": "WEB01 and AZURE01 when SSH port 22 is down",
        "summary": "The playbook must not run while the management channel is down.",
        "steps": (
            "Check that SSH on port 22 answers from MON01.",
            "Restore power, network, and the ansible user key before any restart.",
            "Trigger remediation again only after the management pre-check is up.",
        ),
    },
    "app-verification-failed": {
        "title": "App verification failed",
        "applies": "APP01 after restart_container",
        "summary": "The container command finished, but the app port did not pass the post-check.",
        "steps": (
            "Check that container app01-web is running.",
            "Confirm the app listens on the expected port.",
            "Read the container log, then trigger the action again.",
        ),
    },
    "app-execution-failed": {
        "title": "App execution failed",
        "applies": "APP01 when the container restart command fails",
        "summary": "The restart command failed before verification.",
        "steps": (
            "Read the job stderr.",
            "Confirm the container name app01-web still exists.",
            "Fix the runtime error, then trigger the action again.",
        ),
    },
    "app-management-blocked": {
        "title": "App management channel blocked",
        "applies": "APP01 when SSH port 22 is down",
        "summary": "The playbook must not run while SSH is down.",
        "steps": (
            "Restore SSH from MON01 to APP01.",
            "Trigger remediation again after the management pre-check passes.",
        ),
    },
    "windows-exporter-verification-failed": {
        "title": "Windows Exporter verification failed",
        "applies": "WIN01 after restart_windows_exporter",
        "summary": "The service start finished, but port 9182 did not pass the post-check.",
        "steps": (
            "Confirm windows_exporter is running and listening on 9182.",
            "Request http://WIN01:9182/metrics from the management host.",
            "Fix the listen port or firewall, then trigger the action again.",
        ),
    },
    "windows-exporter-execution-failed": {
        "title": "Windows Exporter execution failed",
        "applies": "WIN01 when the exporter service fails to start",
        "summary": "The start command failed before verification.",
        "steps": (
            "Read the job stderr and the Windows service state.",
            "Correct the service path, then trigger the action again.",
        ),
    },
    "windows-exporter-management-blocked": {
        "title": "Windows Exporter management channel blocked",
        "applies": "WIN01 when WinRM port 5985 is down",
        "summary": "The playbook must not run while WinRM is down.",
        "steps": (
            "Restore WinRM on port 5985.",
            "Trigger remediation again after the management pre-check passes.",
        ),
    },
}


ACTION_RUNBOOKS = {
    "restart_nginx": "restart-nginx",
    "restart_container": "restart-app-container",
    "restart_windows_exporter": "restart-windows-exporter",
    "restart_docker_service": "restart-docker-service",
    "reboot_server": "reboot-azure01",
    "investigate": "manual-investigation",
}

RUNBOOKS.update(
    {
        "restart-nginx": {
            "title": "Restart Nginx",
            "risk": "low",
            "applies": "WEB01 uses restart-nginx.yml. AZURE01 uses restart-azure-nginx.yml.",
            "summary": "The incident shows the risk stored for this action. LOW runs after the usual pre-check. It does not open an approval request.",
            "steps": (
                "Confirm the target and the Nginx HTTP check.",
                "Run the action from the incident when the risk is LOW.",
                "Read the job log if verification does not return HTTP 200.",
            ),
        },
        "restart-app-container": {
            "title": "Restart container",
            "risk": "low",
            "applies": "APP01, container app01-web, playbook restart-app-container.yml.",
            "summary": "The incident shows the risk stored for this action. LOW runs after the usual pre-check. It does not open an approval request.",
            "steps": (
                "Confirm APP01 and container app01-web.",
                "Run the action from the incident when the risk is LOW.",
                "The post-check expects HTTP 200 on port 8080.",
            ),
        },
        "restart-windows-exporter": {
            "title": "Restart Windows Exporter",
            "risk": "low",
            "applies": "WIN01, service windows_exporter, playbook restart-windows-exporter.yml.",
            "summary": "The incident shows the risk stored for this action. LOW runs after the usual pre-check. It does not open an approval request.",
            "steps": (
                "Confirm WinRM is up before the playbook starts.",
                "Run the action from the incident when the risk is LOW.",
                "The post-check expects HTTP 200 on port 9182.",
            ),
        },
        "restart-docker-service": {
            "title": "Restart Docker",
            "risk": "medium",
            "applies": "APP01, playbook restart-docker-service.yml.",
            "summary": "The incident shows the risk stored for this action. MEDIUM waits for an admin. The playbook does not start while the request is pending, rejected, or expired.",
            "steps": (
                "An operator or an admin requests approval from the incident.",
                "An admin approves or rejects on the approval page.",
                "A valid approval creates one job. Docker must be active, the container running, and HTTP 200.",
            ),
        },
        "reboot-azure01": {
            "title": "Reboot server",
            "risk": "high",
            "applies": "AZURE01, playbook reboot-azure01.yml.",
            "summary": "The incident shows the risk stored for this action. HIGH can be requested only by an admin, and only an admin can approve it.",
            "steps": (
                "An admin requests approval from the incident.",
                "An admin approves on the approval page before the reboot playbook starts.",
                "Verification waits until SSH and Nginx HTTP 200 answer again.",
            ),
        },
        "docker-verification-failed": {
            "title": "Docker verification failed",
            "applies": "APP01 after restart_docker_service",
            "summary": "The Docker command finished, but the service, container, or HTTP 200 check failed. Do not retry automatically.",
            "steps": (
                "Check that the Docker service is active and app01-web is running.",
                "Request HTTP 200 on port 8080.",
                "Keep the failed job. A later recovery does not rewrite it.",
            ),
        },
        "docker-execution-failed": {
            "title": "Docker execution failed",
            "applies": "APP01 when restarting the Docker service fails",
            "summary": "The remediation command failed. Auto policy retries once. A manual run does not retry by itself.",
            "steps": (
                "Read the job stderr.",
                "Restore the Docker service, then request the action again.",
            ),
        },
        "docker-management-blocked": {
            "title": "Docker management channel blocked",
            "applies": "APP01 when SSH port 22 is down",
            "summary": "The playbook must not run while SSH is down.",
            "steps": (
                "Restore SSH from MON01 to APP01.",
                "Request the action again after the management pre-check passes.",
            ),
        },
        "reboot-verification-failed": {
            "title": "Reboot verification failed",
            "applies": "AZURE01 after reboot_server",
            "summary": "The reboot command finished, but SSH or Nginx HTTP 200 did not return in time.",
            "steps": (
                "Wait for SSH on port 22, then request the Nginx URL.",
                "Do not mark the failed job as success if the host answers later.",
            ),
        },
        "reboot-execution-failed": {
            "title": "Reboot execution failed",
            "applies": "AZURE01 when the reboot playbook fails",
            "summary": "The reboot command failed. A manual run does not retry by itself.",
            "steps": (
                "Read the job stderr.",
                "Request a new approval only after the host can be reached.",
            ),
        },
        "reboot-management-blocked": {
            "title": "Reboot management channel blocked",
            "applies": "AZURE01 when SSH port 22 is down",
            "summary": "The playbook must not run while SSH is down.",
            "steps": (
                "Restore SSH to AZURE01 from MON01.",
                "Request the reboot again after the management pre-check passes.",
            ),
        },
        "manual-investigation": {
            "title": "Manual investigation",
            "applies": "A firing alert whose cause does not match a runbook.",
            "summary": "No remediation action is selected until the cause is known. The playbook is not started.",
            "steps": (
                "Read the alert name and confirm which service is down.",
                "Open the matching runbook only after the cause is identified.",
                "Leave the incident open until that service check recovers.",
            ),
        },
    }
)

# One map for auto, manual, and retry. Risk stays on the action runbook.
# A host that does not answer, or a generic service_down, is not reboot_required.
RUNBOOK_MAP = (
    {"host": "WEB01", "incident_type": "nginx_down", "action": "restart_nginx"},
    {"host": "APP01", "incident_type": "container_down", "action": "restart_container"},
    {"host": "APP01", "incident_type": "docker_service_down", "action": "restart_docker_service"},
    {"host": "WIN01", "incident_type": "exporter_down", "action": "restart_windows_exporter"},
    {"host": "AZURE01", "incident_type": "nginx_down", "action": "restart_nginx"},
    {"host": "AZURE01", "incident_type": "reboot_required", "action": "reboot_server"},
)

# container_down is valid only while Docker is active. The replacement is another row in RUNBOOK_MAP.
_REQUIRES_ACTIVE = {
    "container_down": {"service": "docker", "when_inactive": "docker_service_down"},
}

_SIGNALS = {
    "nginxdown": "nginx_down",
    "azurenginxdown": "nginx_down",
    "containerdown": "container_down",
    "dockerservicedown": "docker_service_down",
    "dockerdown": "docker_service_down",
    "windowsexporterdown": "exporter_down",
    "exporterdown": "exporter_down",
    "rebootrequired": "reboot_required",
}


# Probe labels, most specific first. Docker is before the app port so a dead daemon
# is not reported as a container outage.
_PROBE_SIGNALS = (
    ("docker", "docker_service_down"),
    ("nginx", "nginx_down"),
    ("exporter", "exporter_down"),
    ("container", "container_down"),
    ("app", "container_down"),
)


def cause_token(alert_name):
    return re.sub(r"[^a-z0-9]", "", (alert_name or "").lower())


def observed_docker_active(host):
    """True or False when the probe names Docker. None when this sweep did not look."""
    for item in (host or {}).get("services") or []:
        if "docker" in cause_token(item.get("name") or ""):
            return (item.get("status") or "").upper() == "UP"
    return None


def probe_incident_type(host):
    """Incident type named by a down probe. A generic outage is not reboot_required."""
    down = [
        item.get("name") or ""
        for item in (host or {}).get("services") or []
        if (item.get("status") or "").upper() == "DOWN"
    ]
    for needle, incident_type in _PROBE_SIGNALS:
        for name in down:
            if needle in cause_token(name):
                return incident_type
    if ((host or {}).get("exporter") or "").upper() == "DOWN":
        return "exporter_down"
    return None


def incident_signal(alert_name):
    """Canonical incident type named by an alert. Generic down signals stay unknown."""
    return _SIGNALS.get(cause_token(alert_name))


def incident_type_for_action(server_name, action_key):
    host = (server_name or "").upper()
    for row in RUNBOOK_MAP:
        if row["host"] == host and row["action"] == action_key:
            return row["incident_type"]
    return None


def classify_incident(server_name, alert_name=None, *, management_down=False, docker_active=True, requested_action=None):
    """Pre-check management and Docker, then read RUNBOOK_MAP. No host is special-cased here."""
    if management_down:
        return {
            "incident_type": "management_unavailable",
            "action_key": None,
            "blocked": True,
            "investigate": False,
        }
    incident_type = incident_signal(alert_name)
    if incident_type is None and requested_action:
        incident_type = incident_type_for_action(server_name, requested_action)
    dependency = _REQUIRES_ACTIVE.get(incident_type)
    if dependency and dependency["service"] == "docker" and not docker_active:
        incident_type = dependency["when_inactive"]
    if incident_type is None:
        return {
            "incident_type": "unknown_issue",
            "action_key": None,
            "blocked": False,
            "investigate": True,
        }
    host = (server_name or "").upper()
    row = next((item for item in RUNBOOK_MAP if item["host"] == host and item["incident_type"] == incident_type), None)
    if row is None:
        return {
            "incident_type": "unknown_issue",
            "action_key": None,
            "blocked": False,
            "investigate": True,
        }
    return {
        "incident_type": row["incident_type"],
        "action_key": row["action"],
        "blocked": False,
        "investigate": False,
    }


def classify_action(server_name, alert_name):
    """Action key for a classified alert, or None when the cause is unknown."""
    plan = classify_incident(server_name, alert_name)
    return plan["action_key"]


def mapped_actions(server_name):
    """Actions the runbook map allows on this target. Risk comes from the same runbook."""
    host = (server_name or "").upper()
    found = []
    seen = set()
    for row in RUNBOOK_MAP:
        if row["host"] != host or row["action"] in seen:
            continue
        seen.add(row["action"])
        page = action_runbook(row["action"])
        found.append(
            {
                "action_key": row["action"],
                "incident_type": row["incident_type"],
                "label": page["title"] if page else row["action"],
                "risk": risk_for(row["action"]) or "low",
            }
        )
    return found


def risk_for(action_key):
    """Risk stored on the action runbook. Approval and the incident page both read this."""
    page = action_runbook(action_key)
    if page is None:
        return None
    risk = (page.get("risk") or "").lower()
    if risk in {"low", "medium", "high"}:
        return risk
    return None


def action_runbook(action_key):
    slug = ACTION_RUNBOOKS.get(action_key)
    if slug is None:
        return None
    return runbook_page(slug)


def runbook_for(action_key, final_status):
    prefix = {
        "restart_nginx": "nginx",
        "restart_container": "app",
        "restart_windows_exporter": "windows-exporter",
        "restart_docker_service": "docker",
        "reboot_server": "reboot",
    }.get(action_key)
    suffix = {
        "VERIFICATION_FAILED": "verification-failed",
        "EXECUTION_FAILED": "execution-failed",
        "MANAGEMENT_BLOCKED": "management-blocked",
        "BLOCKED": "management-blocked",
        "MANUAL_REQUIRED": "execution-failed",
    }.get(final_status)
    if not prefix or not suffix:
        return None
    return runbook_page(f"{prefix}-{suffix}")


def runbook_page(slug):
    page = RUNBOOKS.get(slug)
    if page is None:
        return None
    return {"slug": slug, **page}
