"""Short operator runbooks linked from a manual-required job."""

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


def runbook_for(action_key, final_status):
    prefix = {
        "restart_nginx": "nginx",
        "restart_container": "app",
        "restart_windows_exporter": "windows-exporter",
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
