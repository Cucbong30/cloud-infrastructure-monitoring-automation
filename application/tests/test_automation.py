from sqlalchemy import func, select

from app.executors.ansible import AnsibleRunnerExecutor
from app.executors.base import ExecutionResult
from app.executors.powershell import PowerShellExecutor
from app.executors.shell import ShellExecutor
from app.extensions import db
from app.models import AutomationJob, Server, User, utcnow
from app.services.automation import AutomationRejected, dispatch, enqueue_job, scrub_output, validate_parameters
from tests.conftest import login, post_csrf


def test_mock_job_reaches_success_and_failure(seeded):
    class Probe:
        seen = None

        def execute(self, job, server, action_definition):
            Probe.seen = job.status
            return ExecutionResult(True, 0, "probe ok", utcnow(), utcnow())

    with seeded.app_context():
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        original = seeded.config["AUTOMATION_EXECUTOR"]
        seeded.config["AUTOMATION_EXECUTOR"] = "mock"
        import app.services.automation as automation_service

        previous = automation_service.get_executor
        automation_service.get_executor = lambda name: Probe
        try:
            job = enqueue_job(
                server_id=server.id,
                action_key="restart_nginx",
                parameters={"simulate": "success"},
                trigger_source="manual",
                requested_by=operator.id,
            )
            assert job.status == "queued"
            finished = dispatch(job.id, actor=operator)
        finally:
            automation_service.get_executor = previous
            seeded.config["AUTOMATION_EXECUTOR"] = original
        assert Probe.seen == "running"
        assert finished.status == "succeeded"
        assert finished.exit_code == 0

        failed = enqueue_job(
            server_id=server.id,
            action_key="restart_nginx",
            parameters={"simulate": "fail"},
            trigger_source="manual",
            requested_by=operator.id,
        )
        failed = dispatch(failed.id, actor=operator)
        assert failed.status == "failed"
        assert failed.exit_code == 1


def test_allow_list_rejects_commands_and_unknown_actions():
    for action_key, parameters in (
        ("restart_nginx", {"command": "id"}),
        ("restart_nginx", {"playbook": "automation-ansible"}),
        ("rm-rf", {}),
        ("~/ansible/playbooks/restart-nginx.yml", {}),
    ):
        try:
            validate_parameters(action_key, parameters)
        except AutomationRejected:
            continue
        raise AssertionError(action_key)


def test_http_rejects_raw_command_and_playbook_path(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server_id = db.session.scalar(select(Server.id).where(Server.name == "web-01"))
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
    rejected_command = post_csrf(
        client,
        "/automation/jobs",
        {
            "server_id": str(server_id),
            "action_key": "restart_nginx",
            "command": "id",
            "simulate": "success",
        },
        page="/automation/",
    )
    rejected_action = post_csrf(
        client,
        "/automation/jobs",
        {
            "server_id": str(server_id),
            "action_key": "~/ansible/playbooks/restart-nginx.yml",
            "simulate": "success",
        },
        page="/automation/",
    )
    assert rejected_command.status_code == 400
    assert rejected_action.status_code == 400
    with seeded.app_context():
        db.session.expire_all()
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before


def test_output_is_scrubbed_and_truncated(seeded):
    class SecretExecutor:
        def execute(self, job, server, action_definition):
            output = "password=hunter2\nall good\nAuthorization: Bearer abc\n" + ("x" * 50)
            return ExecutionResult(True, 0, output, utcnow(), utcnow())

    with seeded.app_context():
        seeded.config["JOB_OUTPUT_MAX_CHARS"] = 30
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        import app.services.automation as automation_service

        previous = automation_service.get_executor
        automation_service.get_executor = lambda name: SecretExecutor
        try:
            job = enqueue_job(
                server_id=server.id,
                action_key="restart_nginx",
                parameters={},
                trigger_source="manual",
                requested_by=operator.id,
            )
            finished = dispatch(job.id, actor=operator)
        finally:
            automation_service.get_executor = previous
        assert "hunter2" not in finished.output_excerpt
        assert "[redacted]" in finished.output_excerpt
        assert "all good" in finished.output_excerpt
        assert finished.output_excerpt.endswith("[truncated]")
        assert scrub_output("token=abc", 100) == "[redacted]"


def test_future_executors_do_not_run_real_commands():
    for executor in (AnsibleRunnerExecutor(), PowerShellExecutor(), ShellExecutor()):
        result = executor.execute(None, None, None)
        assert result.success is False
        assert "disabled" in result.output.lower()


def test_ansible_runs_only_the_allow_listed_playbook(seeded, monkeypatch):
    calls = {}

    def fake_run(**kwargs):
        calls.update(kwargs)
        return ExecutionResult(True, 0, "nginx restarted", utcnow(), utcnow())

    monkeypatch.setattr("app.executors.ansible.run_controller_playbook", fake_run)
    with seeded.app_context():
        seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
        seeded.config["ANSIBLE_CONTROLLER_USER"] = "lab"
        seeded.config["ANSIBLE_CONTROLLER_HOST"] = "192.168.10.10"
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        job = enqueue_job(
            server_id=server.id,
            action_key="restart_nginx",
            parameters={},
            trigger_source="manual",
            requested_by=operator.id,
        )
        finished = dispatch(job.id, actor=operator)
        assert finished.status == "succeeded"
    assert calls["playbook"] == "~/ansible/playbooks/restart-nginx.yml"
    assert calls["host"] == "192.168.10.10"
    assert calls["user"] == "lab"


def test_ansible_failure_and_executor_crash_stay_on_the_job(seeded, monkeypatch):
    def fake_run(**kwargs):
        return ExecutionResult(False, 4, "WEB01 unreachable", utcnow(), utcnow())

    monkeypatch.setattr("app.executors.ansible.run_controller_playbook", fake_run)
    with seeded.app_context():
        seeded.config["AUTOMATION_EXECUTOR"] = "ansible"
        operator = db.session.scalar(select(User).where(User.username == "operator"))
        server = db.session.scalar(select(Server).where(Server.name == "APP01"))
        job = enqueue_job(
            server_id=server.id,
            action_key="restart_container",
            parameters={"container_name": "app01-web"},
            trigger_source="manual",
            requested_by=operator.id,
        )
        failed = dispatch(job.id, actor=operator)
        assert failed.status == "failed"
        assert "unreachable" in failed.output_excerpt

        import app.services.automation as automation_service

        class Boom:
            def execute(self, job, server, action_definition):
                raise RuntimeError("boom")

        previous = automation_service.get_executor
        automation_service.get_executor = lambda name: Boom
        try:
            crashed = enqueue_job(
                server_id=server.id,
                action_key="restart_container",
                parameters={"container_name": "app01-web"},
                trigger_source="manual",
                requested_by=operator.id,
            )
            crashed = dispatch(crashed.id, actor=operator)
        finally:
            automation_service.get_executor = previous
        assert crashed.status == "failed"
        assert crashed.output_excerpt == "Executor failed without a result."


def test_server_page_can_trigger_nginx_remediation(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        server.status = "warning"
        db.session.commit()
        server_id = server.id
    page = client.get(f"/servers/{server_id}")
    assert b"Restart Nginx" in page.data
    response = post_csrf(client, f"/servers/{server_id}/remediate", {}, page=f"/servers/{server_id}")
    assert response.status_code == 302
    with seeded.app_context():
        job = db.session.scalar(select(AutomationJob).order_by(AutomationJob.id.desc()))
        assert job.action_key == "restart_nginx"
        assert job.status == "succeeded"


def test_unreachable_server_shows_notice_instead_of_restart(seeded, client):
    login(client, "operator")
    with seeded.app_context():
        server = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        server.status = "down"
        db.session.commit()
        server_id = server.id
        before = db.session.scalar(select(func.count()).select_from(AutomationJob))
    page = client.get(f"/servers/{server_id}")
    assert b"Restart Nginx cannot run" in page.data
    assert b">Restart Nginx<" not in page.data
    response = post_csrf(client, f"/servers/{server_id}/remediate", {}, page=f"/servers/{server_id}")
    assert response.status_code == 302
    with seeded.app_context():
        assert db.session.scalar(select(func.count()).select_from(AutomationJob)) == before
    jobs = client.get("/automation/")
    assert b"WEB01 is unreachable" in jobs.data


def test_unreachable_dashboard_event_is_a_single_message(seeded):
    from app.blueprints.dashboard import _annotate_problem, _host_events

    host = {
        "name": "WEB01",
        "status": "Unreachable",
        "exporter": "DOWN",
        "exporter_label": "Node Exporter :9100",
        "instance": "192.168.10.11:9100",
        "services": [{"name": "Nginx :80", "status": "DOWN", "latency_ms": None}],
        "last_seen": None,
    }
    with seeded.app_context():
        _annotate_problem(host)
        events = _host_events("WEB01", host)
    assert "are both down" in host["problem"]
    probe = [event for event in events if event["source"] == "probe"]
    assert len(probe) == 1
    assert probe[0]["title"] == "Host unreachable"
