import os
import subprocess
import time

from flask import current_app

from app.executors.actions import ACTIONS, LAB_TARGETS
from app.executors.base import AutomationExecutor, ExecutionResult
from app.models import utcnow
from app.validation import TOKEN_RE

CONTROLLER_HOST = "192.168.10.10"
_PORT_CACHE = {}
_PORT_CACHE_SECONDS = 10
_MANAGEMENT_PORTS = {
    ("192.168.10.11", 22),
    ("192.168.10.12", 22),
    ("192.168.10.13", 5985),
}


def controller_port_open(host, port, timeout=2):
    """TCP check from MON01. Ansible uses that path, not the portal machine."""
    host = str(host or "")
    try:
        port = int(port)
    except (TypeError, ValueError):
        return False, None
    if (host, port) not in _MANAGEMENT_PORTS:
        return False, None
    now = time.monotonic()
    cached = _PORT_CACHE.get((host, port))
    if cached is not None and now - cached[0] < _PORT_CACHE_SECONDS:
        return cached[1], None
    config = current_app.config
    user = (config.get("ANSIBLE_CONTROLLER_USER") or "").strip()
    controller = (config.get("ANSIBLE_CONTROLLER_HOST") or CONTROLLER_HOST).strip()
    key_file = (config.get("ANSIBLE_CONTROLLER_KEY") or "").strip()
    if controller != CONTROLLER_HOST or not TOKEN_RE.fullmatch(user or ""):
        _PORT_CACHE[(host, port)] = (now, False)
        return False, None
    seconds = max(1, min(int(timeout or 2), 10))
    remote = f"timeout {seconds} bash -c 'echo >/dev/tcp/{host}/{port}'"
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=10",
    ]
    if key_file:
        command.extend(["-i", key_file])
    command.extend([f"{user}@{controller}", remote])
    try:
        completed = subprocess.run(
            command,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=seconds + 15,
            check=False,
        )
        ok = completed.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        ok = False
    _PORT_CACHE[(host, port)] = (time.monotonic(), ok)
    return ok, None


def allowed_parameters(server, action_key, parameters):
    spec = LAB_TARGETS.get(action_key)
    if spec is None or server is None or not isinstance(parameters, dict):
        return False
    name, ip, required = spec
    if getattr(server, "name", None) != name or getattr(server, "ip_address", None) != ip:
        return False
    return all(parameters.get(key) == value for key, value in required.items())


def run_controller_playbook(*, user, host, key_file, playbook, timeout):
    started = utcnow()
    allowed = {item.playbook for item in ACTIONS.values()}
    if host != CONTROLLER_HOST or playbook not in allowed:
        return ExecutionResult(False, 1, "Playbook is not allow-listed.", started, utcnow())
    if not TOKEN_RE.fullmatch(user or ""):
        return ExecutionResult(False, 1, "Ansible controller user is not configured.", started, utcnow())
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        "-o",
        "ConnectTimeout=10",
    ]
    if key_file:
        command.extend(["-i", key_file])
    command.extend([f"{user}@{host}", "ansible-playbook", playbook])
    try:
        completed = subprocess.run(
            command,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = (exc.stdout or "").strip()
        stderr = "\n".join(part for part in (exc.stderr, "Ansible timed out.") if part).strip()
        return ExecutionResult(False, 124, stdout, started, utcnow(), stderr)
    except FileNotFoundError:
        return ExecutionResult(False, 127, "", started, utcnow(), "ssh is not installed.")
    except OSError as exc:
        return ExecutionResult(False, 1, "", started, utcnow(), f"Could not start ssh ({exc.__class__.__name__}).")
    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    if not stdout and not stderr:
        stdout = f"ansible-playbook on MON01 exited {completed.returncode}."
    return ExecutionResult(completed.returncode == 0, completed.returncode, stdout, started, utcnow(), stderr)


class AnsibleRunnerExecutor(AutomationExecutor):
    """SSH to MON01 and run one fixed playbook. Failures stay on the job."""

    def execute(self, job, server, action_definition):
        started = utcnow()
        if job is None or server is None or action_definition is None:
            return ExecutionResult(False, 1, "Real Ansible execution is disabled for this request.", started, started)
        try:
            import json

            parameters = json.loads(job.parameters_json or "{}")
            if not allowed_parameters(server, action_definition.key, parameters):
                return ExecutionResult(False, 1, "Action is not allowed for this server.", started, utcnow())
            if action_definition.playbook != ACTIONS[action_definition.key].playbook:
                return ExecutionResult(False, 1, "Playbook is not allow-listed.", started, utcnow())
            config = current_app.config
            return run_controller_playbook(
                user=(config.get("ANSIBLE_CONTROLLER_USER") or "").strip(),
                host=(config.get("ANSIBLE_CONTROLLER_HOST") or CONTROLLER_HOST).strip(),
                key_file=(config.get("ANSIBLE_CONTROLLER_KEY") or "").strip(),
                playbook=action_definition.playbook,
                timeout=int(config.get("ANSIBLE_TIMEOUT_SECONDS") or 90),
            )
        except Exception:
            return ExecutionResult(False, 1, "Ansible failed before the playbook finished.", started, utcnow())
