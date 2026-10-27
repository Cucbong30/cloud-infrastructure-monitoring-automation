import os
import subprocess

from flask import current_app

from app.executors.actions import ACTIONS, LAB_TARGETS
from app.executors.base import AutomationExecutor, ExecutionResult
from app.models import utcnow
from app.validation import TOKEN_RE

CONTROLLER_HOST = "192.168.10.10"


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
        output = "\n".join(part for part in (exc.stdout, exc.stderr) if part).strip()
        return ExecutionResult(False, 124, (output + "\nAnsible timed out.").strip(), started, utcnow())
    except FileNotFoundError:
        return ExecutionResult(False, 127, "ssh is not installed.", started, utcnow())
    except OSError as exc:
        return ExecutionResult(False, 1, f"Could not start ssh ({exc.__class__.__name__}).", started, utcnow())
    output = "\n".join(part for part in (completed.stdout, completed.stderr) if part).strip()
    if not output:
        output = f"ansible-playbook on MON01 exited {completed.returncode}."
    return ExecutionResult(completed.returncode == 0, completed.returncode, output, started, utcnow())


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
