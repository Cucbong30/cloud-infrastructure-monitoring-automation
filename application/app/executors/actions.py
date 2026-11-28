from dataclasses import dataclass


@dataclass(frozen=True)
class ActionDefinition:
    key: str
    playbook: str
    params: tuple[str, ...]
    dry_run: bool = False
    risk: str = "low"


# Playbooks live on the Ansible controller MON01. The portal never accepts a path from the user.
ACTIONS = {
    "restart_nginx": ActionDefinition(
        "restart_nginx",
        "~/ansible/playbooks/restart-nginx.yml",
        (),
        risk="low",
    ),
    "restart_container": ActionDefinition(
        "restart_container",
        "~/ansible/playbooks/restart-app-container.yml",
        ("container_name",),
        risk="low",
    ),
    "restart_windows_exporter": ActionDefinition(
        "restart_windows_exporter",
        "~/ansible/playbooks/restart-windows-exporter.yml",
        ("service_name",),
        risk="low",
    ),
    "restart_docker_service": ActionDefinition(
        "restart_docker_service",
        "~/ansible/playbooks/restart-docker-service.yml",
        (),
        risk="medium",
    ),
    "reboot_server": ActionDefinition(
        "reboot_server",
        "~/ansible/playbooks/reboot-azure01.yml",
        (),
        risk="high",
    ),
}

SERVICE_LABELS = {
    "restart_nginx": "Nginx",
    "restart_container": "App",
    "restart_windows_exporter": "Windows Exporter",
    "restart_docker_service": "Docker",
    "reboot_server": "Host",
}

LAB_TARGETS = {
    "restart_nginx": ("WEB01", "192.168.10.11", {}),
    "restart_container": ("APP01", "192.168.10.12", {"container_name": "app01-web"}),
    "restart_windows_exporter": ("WIN01", "192.168.10.13", {"service_name": "windows_exporter"}),
}


def target_spec(server_name, action_key):
    """One action can run on the local host or on AZURE01. The server name picks the address."""
    name = (server_name or "").upper()
    if name == "AZURE01" and action_key == "restart_nginx":
        from app.services.inventory import azure_settings

        return azure_settings()["ip"], {}
    specs = {
        ("WEB01", "restart_nginx"): ("192.168.10.11", {}),
        ("APP01", "restart_container"): ("192.168.10.12", {"container_name": "app01-web"}),
        ("APP01", "restart_docker_service"): ("192.168.10.12", {}),
        ("WIN01", "restart_windows_exporter"): ("192.168.10.13", {"service_name": "windows_exporter"}),
    }
    if name == "AZURE01" and action_key == "reboot_server":
        from app.services.inventory import azure_settings

        return azure_settings()["ip"], {}
    return specs.get((name, action_key))


def playbook_for(server_name, action_key):
    if (server_name or "").upper() == "AZURE01" and action_key == "restart_nginx":
        from app.services.inventory import azure_settings

        return azure_settings()["playbook"]
    action = ACTIONS.get(action_key)
    return None if action is None else action.playbook

# Controlled failure fixtures on MON01. Exit code 2 is not enough to classify them.
# They stay out of ACTIONS so neither the job form nor auto-remediation can select them.
FAILURE_PLAYBOOKS = {
    ("WEB01", "execution"): "restart-nginx-execution-fail-week6.yml",
    ("WEB01", "verification"): "restart-nginx-verification-fail-week6.yml",
    ("APP01", "execution"): "restart-app-container-execution-fail-week6.yml",
    ("APP01", "verification"): "restart-app-container-verification-fail-week6.yml",
    ("WIN01", "execution"): "restart-windows-exporter-fail-test.yml",
    ("WIN01", "verification"): "restart-windows-exporter-verification-fail.yml",
}

# Capacity warnings and destructive changes stay diagnostic. They are never executed.
DENIED_ACTIONS = frozenset(
    {
        "reboot",
        "restart_host",
        "kill_process",
        "kill",
        "disk_cleanup",
        "cleanup",
        "delete_file",
        "remove_file",
        "network_change",
        "change_network",
    }
)


def action_risk(action_key):
    """LOW runs immediately. MEDIUM and HIGH wait for an admin.

    The runbook registry is the source. The action catalog keeps the same values.
    """
    if action_key in DENIED_ACTIONS:
        return "high"
    from app.services.runbooks import risk_for

    recorded = risk_for(action_key)
    if recorded:
        return recorded
    action = ACTIONS.get(action_key)
    if action is None:
        return "high"
    return action.risk
