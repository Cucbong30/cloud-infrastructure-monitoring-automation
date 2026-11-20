import os
import re
import subprocess
import time

from flask import current_app

from app.executors.actions import ACTIONS, playbook_for, target_spec
from app.executors.base import AutomationExecutor, ExecutionResult
from app.models import utcnow
from app.validation import TOKEN_RE

CONTROLLER_HOST = "192.168.10.10"
CONTROLLER_INVENTORY = "/etc/ansible/hosts"
_PORT_CACHE = {}
_PORT_CACHE_SECONDS = 10
_MANAGEMENT_PORTS = {
    ("192.168.10.11", 22),
    ("192.168.10.12", 22),
    ("192.168.10.13", 5985),
}


def _local_identity(key_file):
    """Pass -i only for a key file on this machine. Target keys stay in the Ansible inventory."""
    path = (key_file or "").strip()
    if path and os.path.isfile(path):
        return ["-i", path]
    return []


def controller_port_open(host, port, timeout=2):
    """TCP check from MON01. Ansible uses that path, not the portal machine."""
    host = str(host or "")
    try:
        port = int(port)
    except (TypeError, ValueError):
        return False, None
    if not _management_allowed(host, port):
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
        "ConnectTimeout=4",
    ]
    command.extend(_local_identity(key_file))
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


_TASK_HEADER = re.compile(r"^TASK \[(?P<name>[^\]]+)\]", re.MULTILINE)
_TASK_RESULT = re.compile(r"^(?P<kind>ok|changed|failed|fatal|unreachable|skipping)\s*:", re.IGNORECASE | re.MULTILINE)


def playbook_failure_stage(output, stderr=""):
    """Return verification_failed when the fix task passed and a later check task failed.

    A non-zero ansible-playbook exit code is an execution failure only when the
    remediation task itself failed. Waiting for the service port is a post-check.
    """
    tasks = _playbook_tasks(f"{output or ''}\n{stderr or ''}")
    if not tasks:
        return None, None
    remediation = [task for task in tasks if not _is_verification_task(task["name"])]
    verification = [task for task in tasks if _is_verification_task(task["name"])]
    remediation_failed = any(task["result"] in {"failed", "unreachable"} for task in remediation)
    remediation_ok = any(task["result"] in {"ok", "changed"} for task in remediation)
    failed_check = next(
        (task for task in verification if task["result"] in {"failed", "unreachable"}),
        None,
    )
    if remediation_ok and failed_check is not None and not remediation_failed:
        return "verification_failed", failed_check["name"]
    if remediation_failed:
        failed = next(task for task in remediation if task["result"] in {"failed", "unreachable"})
        return "execution_failed", failed["name"]
    return None, None


def _playbook_tasks(text):
    headers = list(_TASK_HEADER.finditer(text))
    tasks = []
    for index, header in enumerate(headers):
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        body = text[header.end() : end]
        found = list(_TASK_RESULT.finditer(body))
        kind = found[-1].group("kind").lower() if found else None
        if kind == "fatal":
            kind = "failed"
        elif kind is None and re.search(r"\bFAILED!\b", body):
            kind = "failed"
        tasks.append({"name": header.group("name").strip(), "result": kind})
    return tasks


def _is_verification_task(name):
    return re.search(
        r"\b(wait|verify|verification|post-check|postcheck|health|probe|listen|http|uri|url)\b",
        name or "",
        re.IGNORECASE,
    ) is not None


def _management_allowed(host, port):
    if (host, port) in _MANAGEMENT_PORTS:
        return True
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            azure = (current_app.config.get("AZURE01_IP") or "").strip()
            if azure and (host, port) == (azure, 22):
                return True
    except RuntimeError:
        return False
    return False


def allowed_parameters(server, action_key, parameters):
    if server is None or not isinstance(parameters, dict):
        return False
    spec = target_spec(getattr(server, "name", None), action_key)
    if spec is None:
        return False
    ip, required = spec
    if getattr(server, "ip_address", None) != ip:
        return False
    return all(parameters.get(key) == value for key, value in required.items())


def run_controller_playbook(*, user, host, key_file, playbook, timeout):
    started = utcnow()
    allowed = {item.playbook for item in ACTIONS.values()}
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            extra = (current_app.config.get("AZURE01_PLAYBOOK") or "").strip()
            if extra:
                allowed.add(extra)
    except RuntimeError:
        pass
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
    command.extend(_local_identity(key_file))
    command.extend([f"{user}@{host}", "ansible-playbook", "-i", CONTROLLER_INVENTORY, playbook])
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
            playbook = playbook_for(server.name, action_definition.key)
            if playbook is None:
                return ExecutionResult(False, 1, "Playbook is not allow-listed.", started, utcnow())
            config = current_app.config
            return run_controller_playbook(
                user=(config.get("ANSIBLE_CONTROLLER_USER") or "").strip(),
                host=(config.get("ANSIBLE_CONTROLLER_HOST") or CONTROLLER_HOST).strip(),
                key_file=(config.get("ANSIBLE_CONTROLLER_KEY") or "").strip(),
                playbook=playbook,
                timeout=int(config.get("ANSIBLE_TIMEOUT_SECONDS") or 90),
            )
        except Exception:
            return ExecutionResult(False, 1, "Ansible failed before the playbook finished.", started, utcnow())
