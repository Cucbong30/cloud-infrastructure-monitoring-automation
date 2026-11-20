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
}

SERVICE_LABELS = {
    "restart_nginx": "Nginx",
    "restart_container": "App",
    "restart_windows_exporter": "Windows Exporter",
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
        ("WIN01", "restart_windows_exporter"): ("192.168.10.13", {"service_name": "windows_exporter"}),
    }
    return specs.get((name, action_key))


def playbook_for(server_name, action_key):
    if (server_name or "").upper() == "AZURE01" and action_key == "restart_nginx":
        from app.services.inventory import azure_settings

        return azure_settings()["playbook"]
    action = ACTIONS.get(action_key)
    return None if action is None else action.playbook

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
    """LOW actions may run automatically. MEDIUM and HIGH stay manual."""
    if action_key in DENIED_ACTIONS:
        return "high"
    action = ACTIONS.get(action_key)
    if action is None:
        return "high"
    return action.risk
