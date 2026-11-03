from dataclasses import dataclass


@dataclass(frozen=True)
class ActionDefinition:
    key: str
    playbook: str
    params: tuple[str, ...]
    dry_run: bool = False


# Playbooks live on the Ansible controller MON01. The portal never accepts a path from the user.
ACTIONS = {
    "restart_nginx": ActionDefinition(
        "restart_nginx",
        "~/ansible/playbooks/restart-nginx.yml",
        (),
    ),
    "restart_container": ActionDefinition(
        "restart_container",
        "~/ansible/playbooks/restart-app-container.yml",
        ("container_name",),
    ),
    "restart_windows_exporter": ActionDefinition(
        "restart_windows_exporter",
        "~/ansible/playbooks/restart-windows-exporter.yml",
        ("service_name",),
    ),
}

LAB_TARGETS = {
    "restart_nginx": ("WEB01", "192.168.10.11", {}),
    "restart_container": ("APP01", "192.168.10.12", {"container_name": "app01-web"}),
    "restart_windows_exporter": ("WIN01", "192.168.10.13", {"service_name": "windows_exporter"}),
}
