from sqlalchemy import select

from app.extensions import db
from app.models import Alert, Server, utcnow
from app.services.entra import role_from_claims
from app.services.remediation import suggest_remediation
from tests.conftest import login


def test_entra_role_comes_from_the_token():
    assert role_from_claims({"roles": ["Operator"]}) == "operator"
    assert role_from_claims({"roles": ["Admin", "Viewer"]}) == "admin"
    assert role_from_claims({"roles": []}) == "viewer"
    assert role_from_claims({}) == "viewer"


def test_microsoft_button_is_primary_when_sso_is_configured(client):
    client.application.config["ENTRA_TENANT_ID"] = "tenant"
    client.application.config["ENTRA_CLIENT_ID"] = "client"
    client.application.config["ENTRA_CLIENT_SECRET"] = "secret"
    page = client.get("/login")
    assert page.status_code == 200
    assert b"Sign in with Microsoft" in page.data
    assert b"Lab account" in page.data


def test_azure01_is_cloud_and_maps_nginx_to_restart(seeded):
    with seeded.app_context():
        server = db.session.scalar(select(Server).where(Server.name == "AZURE01"))
        assert server is not None
        assert server.environment == "cloud"
        assert server.provider == "azure"
        web = db.session.scalar(select(Server).where(Server.name == "WEB01"))
        assert web.environment == "local"
        assert web.provider == "vmware"
        alert = Alert(
            server_id=server.id,
            fingerprint="azure-nginx-down",
            alert_name="AzureNginxDown",
            source="prometheus",
            severity="critical",
            status="firing",
            summary="Azure Nginx is down",
            starts_at=utcnow(),
            created_at=utcnow(),
        )
        db.session.add(alert)
        db.session.commit()
        suggestion = suggest_remediation(server, alert)
        assert suggestion["action_key"] == "restart_nginx"


def test_notification_includes_the_required_fields(seeded):
    sent = []

    def capture(event, fields, recipients):
        sent.append((event, fields, recipients))

    seeded.config["SMTP_HOST"] = "smtp.office365.com"
    seeded.config["SMTP_USER"] = "monitoring@example.onmicrosoft.com"
    seeded.config["SMTP_PASSWORD"] = "not-a-real-password"
    seeded.config["SMTP_FROM"] = "monitoring@example.onmicrosoft.com"
    seeded.config["NOTIFY_RECIPIENTS"] = "student@example.com"
    seeded.config["NOTIFY_TRANSPORT"] = capture
    with seeded.app_context():
        from app.services.audit import record

        record(
            "incident.created",
            "alert",
            1,
            {
                "target": "AZURE01",
                "action": "restart_nginx",
                "alert_name": "AzureNginxDown",
                "result": "OPEN",
                "message": "Incident opened.",
                "trigger": "auto",
            },
            system=True,
        )
    assert sent[0][0] == "service_down"
    fields = sent[0][1]
    for key in ("target", "service", "alert", "time", "action", "status", "reason"):
        assert fields[key]
    assert fields["target"] == "AZURE01"
    assert fields["service"] == "Nginx"
    assert fields["event"] == "Service Down"
    assert sent[0][2] == ["student@example.com"]


def test_alert_mail_uses_the_distribution_group_for_its_severity(seeded):
    sent = []

    def capture(event, fields, recipients):
        sent.append((event, fields, recipients))

    seeded.config["NOTIFY_TRANSPORT"] = capture
    seeded.config["ALERT_RECIPIENT_CRITICAL"] = "KLTN-Alert-Critical@cucbong.id.vn"
    seeded.config["ALERT_RECIPIENT_WARNING"] = "KLTN-Alert-Warning@cucbong.id.vn"
    seeded.config["ALERT_RECIPIENT_INFO"] = "KLTN-Alert-Info@cucbong.id.vn"
    with seeded.app_context():
        from app.services.notify import send_alert_email

        assert send_alert_email("service_down", "AZURE01", "Nginx", "OPEN", "Nginx is down", action="restart_nginx")
        assert send_alert_email(
            "remediation_success", "AZURE01", "Nginx", "SUCCESS", "Nginx is up", action="restart_nginx"
        )
        assert send_alert_email(
            "verification_failed",
            "AZURE01",
            "Nginx",
            "VERIFICATION_FAILED",
            "post-check on port 80 failed",
            action="restart_nginx",
        )
        assert send_alert_email(
            "manual_required", "AZURE01", "Nginx", "MANUAL_REQUIRED", "retry limit", action="restart_nginx"
        )
        assert send_alert_email("remediation_started", "WEB01", "Nginx", "RUNNING", "started", action="restart_nginx")
    assert sent[0][2] == ["KLTN-Alert-Critical@cucbong.id.vn"]
    assert sent[0][1]["event"] == "Service Down"
    assert sent[1][2] == ["KLTN-Alert-Info@cucbong.id.vn"]
    assert sent[1][1]["severity"] == "info"
    assert sent[2][2] == ["KLTN-Alert-Critical@cucbong.id.vn"]
    assert sent[3][2] == ["KLTN-Alert-Critical@cucbong.id.vn"]
    assert sent[4][2] == ["KLTN-Alert-Warning@cucbong.id.vn"]


def test_graph_sendmail_treats_202_as_accepted(seeded, monkeypatch):
    seeded.config["NOTIFY_ENABLED"] = True
    seeded.config["ENTRA_TENANT_ID"] = "tenant"
    seeded.config["ENTRA_CLIENT_ID"] = "client"
    seeded.config["ENTRA_CLIENT_SECRET"] = "not-a-real-secret"
    seeded.config["GRAPH_SENDER_MAILBOX"] = "portal@example.onmicrosoft.com"
    seeded.config["ALERT_RECIPIENT_CRITICAL"] = "KLTN-Alert-Critical@cucbong.id.vn"
    calls = {}

    class Response:
        status_code = 202

        def json(self):
            return {}

    def fake_post(url, headers, json, timeout):
        calls["url"] = url
        calls["payload"] = json
        return Response()

    monkeypatch.setattr("app.services.notify._graph_token", lambda settings: "token")
    monkeypatch.setattr("app.services.notify.requests.post", fake_post)
    with seeded.app_context():
        from app.services.notify import send_alert_email

        assert send_alert_email("service_down", "AZURE01", "Nginx", "OPEN", "Nginx is down", action="restart_nginx")
    assert calls["url"].endswith("/users/portal%40example.onmicrosoft.com/sendMail")
    assert "/me/sendMail" not in calls["url"]
    assert calls["payload"]["message"]["toRecipients"][0]["emailAddress"]["address"] == (
        "KLTN-Alert-Critical@cucbong.id.vn"
    )
    body = calls["payload"]["message"]["body"]["content"]
    assert calls["payload"]["message"]["body"]["contentType"] == "HTML"
    assert "<table" in body
    assert "#9f1239" in body
    for label in ("Target", "Service", "Event Time", "Event", "Action", "Final Status", "Reason"):
        assert label in body
    for value in ("AZURE01", "Nginx", "Service Down", "systemctl restart nginx", "OPEN"):
        assert value in body
    assert "KLTN Infrastructure Monitoring" in body
    assert "Please do not reply" in body
    from app.services.notify import message_text

    _subject, success = message_text(
        "remediation_success",
        {
            "target": "AZURE01",
            "service": "Nginx",
            "time": "2026-11-06 21:34",
            "event": "Remediation Success",
            "action": "restart_nginx",
            "status": "SUCCESS",
            "reason": "HTTP :80 responded.",
            "severity": "info",
        },
    )
    assert "#047857" in success
    assert "Service Healthy" in success
    assert "[KLTN]" in _subject and "Remediation Success" in _subject
    _subject, warning = message_text(
        "remediation_started",
        {
            "target": "WEB01",
            "service": "Nginx",
            "time": "2026-11-06 21:34",
            "event": "Remediation Started",
            "action": "restart_nginx",
            "status": "RUNNING",
            "reason": "started",
            "severity": "warning",
        },
    )
    assert "#c2410c" in warning


def test_viewer_cannot_open_audit_or_manage_users(seeded, client):
    from tests.conftest import csrf_from

    login(client, "viewer")
    assert client.get("/audit/").status_code == 403
    assert client.get("/users/").status_code == 403
    page = client.get("/dashboard")
    client.post("/logout", data={"csrf_token": csrf_from(page)})
    login(client, "admin")
    page = client.get("/users/")
    assert page.status_code == 200
    assert b"Entra App Role" in page.data
