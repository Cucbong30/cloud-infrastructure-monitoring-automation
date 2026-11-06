"""Mail an incident event through Microsoft Graph, from the generic E5 mailbox.

The token is app-only (client credentials). Mail is sent with
POST /users/{mailbox}/sendMail, never /me/sendMail.
A missing mailbox never blocks remediation.
"""

import html
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote

import requests
from flask import current_app

from app.presentation import format_clock
from app.models import utcnow

EVENT_TITLES = {
    "service_down": "Service Down",
    "remediation_started": "Remediation Started",
    "remediation_success": "Remediation Success",
    "execution_failed": "Execution Failed",
    "verification_failed": "Verification Failed",
    "manual_required": "Manual Required",
    "retry": "Retry",
    "blocked": "Blocked",
    "degraded": "Degraded",
    "resolved": "Resolved",
    "healthy": "Healthy",
}

SEVERITY = {
    "service_down": "critical",
    "execution_failed": "critical",
    "verification_failed": "critical",
    "manual_required": "critical",
    "remediation_started": "warning",
    "retry": "warning",
    "blocked": "warning",
    "degraded": "warning",
    "remediation_success": "info",
    "resolved": "info",
    "healthy": "info",
}

_ACTION_EVENTS = {
    "incident.created": "service_down",
    "auto_remediation.started": "remediation_started",
    "auto_remediation.retry": "retry",
    "auto_remediation.verified": "remediation_success",
    "remediation.verified": "remediation_success",
    "auto_remediation.failed": "execution_failed",
    "remediation.failed": "execution_failed",
    "auto_remediation.verification_failed": "verification_failed",
    "remediation.verification_failed": "verification_failed",
    "manual_intervention.required": "manual_required",
    "auto_remediation.blocked": "blocked",
    "remediation.blocked": "blocked",
    "incident.resolved": "resolved",
}

_SERVICES = {
    "restart_nginx": "Nginx",
    "restart_container": "App",
    "restart_windows_exporter": "Windows Exporter",
}


def _addresses(value):
    return [item.strip() for item in (value or "").split(",") if item.strip()]


def mail_settings():
    config = current_app.config
    graph_sender = (config.get("GRAPH_SENDER_MAILBOX") or config.get("GRAPH_MAIL_SENDER") or "").strip()
    smtp_sender = (config.get("SMTP_FROM") or config.get("SMTP_USER") or "").strip()
    fallback = _addresses(config.get("ALERT_RECIPIENTS") or config.get("NOTIFY_RECIPIENTS"))
    return {
        "host": (config.get("SMTP_HOST") or "").strip(),
        "port": int(config.get("SMTP_PORT") or 587),
        "user": (config.get("SMTP_USER") or "").strip(),
        "password": config.get("SMTP_PASSWORD") or "",
        "sender": graph_sender or smtp_sender,
        "recipients": fallback,
        "routes": {
            "critical": _addresses(config.get("ALERT_RECIPIENT_CRITICAL")),
            "warning": _addresses(config.get("ALERT_RECIPIENT_WARNING")),
            "info": _addresses(config.get("ALERT_RECIPIENT_INFO")),
        },
        "tenant_id": (config.get("ENTRA_TENANT_ID") or "").strip(),
        "client_id": (config.get("ENTRA_CLIENT_ID") or "").strip(),
        "client_secret": config.get("ENTRA_CLIENT_SECRET") or "",
    }


def recipients_for(event_type, settings=None):
    """One distribution group for this event. A flat list is only the fallback."""
    settings = mail_settings() if settings is None else settings
    severity = SEVERITY.get(event_type, "critical")
    routed = settings["routes"].get(severity) or []
    return list(routed or settings["recipients"])


def graph_ready(settings=None):
    settings = mail_settings() if settings is None else settings
    has_recipient = bool(settings["recipients"] or any(settings["routes"].values()))
    return bool(
        settings["tenant_id"]
        and settings["client_id"]
        and settings["client_secret"]
        and settings["sender"]
        and has_recipient
    )


def smtp_ready(settings=None):
    settings = mail_settings() if settings is None else settings
    has_recipient = bool(settings["recipients"] or any(settings["routes"].values()))
    return bool(
        settings["host"]
        and settings["user"]
        and settings["password"]
        and settings["sender"]
        and has_recipient
    )


def mail_ready(settings=None):
    settings = mail_settings() if settings is None else settings
    return graph_ready(settings) or smtp_ready(settings)


def notify_audit(action, details):
    event = _ACTION_EVENTS.get(action)
    if event is None or not isinstance(details, dict):
        return False
    action_key = details.get("action") or details.get("action_key") or ""
    service = _SERVICES.get(action_key, action_key or "—")
    return send_alert_email(
        event,
        details.get("target") or "—",
        service,
        details.get("result") or "—",
        details.get("message") or details.get("reason") or "—",
        action=action_key or "—",
        alert=str(details.get("alert_name") or details.get("alert_id") or "—"),
    )


def send_alert_email(event_type, target, service, status, reason, action="", when=None, alert=""):
    """Send one alert. Graph 202 Accepted means the send was accepted."""
    if event_type not in EVENT_TITLES:
        return False
    settings = mail_settings()
    recipients = recipients_for(event_type, settings)
    if not recipients:
        return False
    fields = {
        "target": target or "—",
        "service": service or "—",
        "alert": alert or "—",
        "time": when or format_clock(utcnow()),
        "event": EVENT_TITLES[event_type],
        "action": action or "—",
        "status": status or "—",
        "reason": reason or "—",
        "severity": SEVERITY.get(event_type, "critical"),
    }
    transport = current_app.config.get("NOTIFY_TRANSPORT")
    if transport is not None:
        transport(event_type, fields, recipients)
        return True
    if not current_app.config.get("NOTIFY_ENABLED"):
        _mail_log("skipped", event_type, recipients, "NOTIFY_ENABLED=false")
        return False
    if not settings["sender"]:
        _mail_log("skipped", event_type, recipients, "GRAPH_SENDER_MAILBOX is empty")
        return False
    try:
        if graph_ready(settings):
            _graph_send(event_type, fields, settings, recipients)
            _mail_log("accepted", event_type, recipients, "Graph 202")
            return True
        if smtp_ready(settings):
            _smtp_send(event_type, fields, settings, recipients)
            _mail_log("accepted", event_type, recipients, "SMTP")
            return True
    except Exception as exc:
        _mail_log("failed", event_type, recipients, str(exc))
        raise
    _mail_log("skipped", event_type, recipients, "mail is not configured")
    return False


def _mail_log(result, event_type, recipients, detail=""):
    """One line in the Flask log and instance/notify.log. No secrets."""
    who = ",".join(recipients) if recipients else "-"
    line = f"{format_clock(utcnow())} {result} event={event_type or '-'} to={who}"
    if detail:
        line = f"{line} {detail}"
    try:
        current_app.logger.info(line)
    except RuntimeError:
        pass
    try:
        folder = Path(current_app.instance_path)
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "notify.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        pass


_ACTION_TEXT = {
    "restart_nginx": "Restart Nginx (systemctl restart nginx)",
    "restart_container": "Restart App container",
    "restart_windows_exporter": "Restart Windows Exporter",
}

_SUMMARIES = {
    "service_down": "The monitored service is not responding.",
    "remediation_started": "Automatic remediation has started.",
    "retry": "The remediation command is being retried once.",
    "remediation_success": "The service has been automatically restored and is now running normally.",
    "execution_failed": "The remediation command failed and could not restore the service.",
    "verification_failed": "The remediation command completed, but the post-check failed.",
    "manual_required": "Automatic recovery stopped. Manual intervention is required.",
    "blocked": "Remediation was blocked before the playbook ran.",
    "degraded": "The target is degraded and needs attention.",
    "resolved": "The incident is resolved and the service is healthy.",
    "healthy": "The service is running normally.",
}

_THEMES = {
    "critical": {
        "title": "#9f1239",
        "banner": "#fff1f2",
        "accent": "#e11d48",
        "mark": "!",
        "subject_mark": "❌",
    },
    "warning": {
        "title": "#c2410c",
        "banner": "#fff7ed",
        "accent": "#ea580c",
        "mark": "!",
        "subject_mark": "⚠️",
    },
    "info": {
        "title": "#047857",
        "banner": "#e8f8ef",
        "accent": "#16a34a",
        "mark": "&#10003;",
        "subject_mark": "✅",
    },
}

_STEP_TONES = {
    "bad": ("#fee2e2", "#dc2626", "!"),
    "run": ("#dbeafe", "#2563eb", "&#9881;"),
    "ok": ("#dcfce7", "#15803d", "&#10003;"),
    "warn": ("#ffedd5", "#c2410c", "!"),
    "wait": ("#f1f5f9", "#94a3b8", "&#183;"),
}

_TIMELINES = {
    "service_down": (
        ("Service Down", "bad", True),
        ("Remediation", "wait", False),
        ("Verification", "wait", False),
        ("Healthy", "wait", False),
    ),
    "remediation_started": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", True),
        ("Verification", "wait", False),
        ("Healthy", "wait", False),
    ),
    "retry": (
        ("Service Down", "bad", False),
        ("Retry", "warn", True),
        ("Verification", "wait", False),
        ("Healthy", "wait", False),
    ),
    "remediation_success": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", False),
        ("Remediation Success", "ok", True),
        ("Service Healthy", "ok", False),
    ),
    "resolved": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", False),
        ("Resolved", "ok", True),
        ("Service Healthy", "ok", False),
    ),
    "healthy": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", False),
        ("Verified", "ok", False),
        ("Service Healthy", "ok", True),
    ),
    "execution_failed": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", False),
        ("Execution Failed", "bad", True),
        ("Manual Required", "warn", False),
    ),
    "verification_failed": (
        ("Service Down", "bad", False),
        ("Remediation Started", "run", False),
        ("Verification Failed", "bad", True),
        ("Manual Required", "warn", False),
    ),
    "manual_required": (
        ("Service Down", "bad", False),
        ("Remediation", "run", False),
        ("Manual Required", "bad", True),
        ("Open", "wait", False),
    ),
    "blocked": (
        ("Service Down", "bad", False),
        ("Blocked", "warn", True),
        ("Playbook Skipped", "wait", False),
        ("Manual Required", "warn", False),
    ),
    "degraded": (
        ("Degraded", "warn", True),
        ("Check", "wait", False),
        ("Remediation", "wait", False),
        ("Healthy", "wait", False),
    ),
}

_STATUS_BADGES = {
    "SUCCESS": ("&#10003;&nbsp;Success", "ok"),
    "HEALTHY": ("&#10003;&nbsp;Healthy", "ok"),
    "RESOLVED": ("&#10003;&nbsp;Resolved", "ok"),
    "VERIFICATION_FAILED": ("Verification Failed", "bad"),
    "EXECUTION_FAILED": ("Execution Failed", "bad"),
    "MANUAL_REQUIRED": ("Manual Required", "bad"),
    "BLOCKED": ("Blocked", "warn"),
    "FAILED": ("Failed", "bad"),
    "RUNNING": ("Running", "run"),
}

_BADGE_COLORS = {
    "ok": ("#16a34a", "#ffffff"),
    "bad": ("#9f1239", "#ffffff"),
    "warn": ("#c2410c", "#ffffff"),
    "run": ("#2563eb", "#ffffff"),
}

_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _event_time(value):
    text = str(value or "").strip()
    try:
        parsed = datetime.strptime(text, "%Y-%m-%d %H:%M")
    except ValueError:
        return text or "—"
    month = _MONTHS[parsed.month - 1]
    return f"{parsed.day} {month} {parsed.year}, {parsed.strftime('%H:%M')} (ICT, UTC+7)"


def _action_label(action):
    key = str(action or "").strip()
    if not key or key == "—":
        return "—"
    return _ACTION_TEXT.get(key, key)


def _badge(label, tone):
    background, foreground = _BADGE_COLORS[tone]
    return (
        f"<span style=\"display:inline-block;background:{background};color:{foreground};"
        f"border-radius:999px;padding:4px 12px;font-size:13px;font-weight:700;\">{label}</span>"
    )


def _status_badge(status, severity_key):
    token = str(status or "—").strip()
    known = _STATUS_BADGES.get(token.upper().replace(" ", "_"))
    if known:
        return _badge(*known)
    tone = {"critical": "bad", "warning": "warn", "info": "ok"}.get(severity_key, "bad")
    return _badge(html.escape(token), tone)


def _detail_table(rows):
    rendered = []
    last = len(rows) - 1
    for index, (icon, label, value_html, emphasize) in enumerate(rows):
        border = "" if index == last else "border-bottom:1px solid #eef2f6;"
        weight = "800" if emphasize else "500"
        rendered.append(
            "<tr>"
            f"<td width=\"40\" valign=\"middle\" style=\"padding:12px 0 12px 16px;{border}"
            f"color:#64748b;font-size:16px;\">{icon}</td>"
            f"<td width=\"132\" valign=\"middle\" style=\"padding:12px 8px;{border}"
            f"color:#64748b;font-size:14px;\">{html.escape(label)}</td>"
            f"<td valign=\"middle\" style=\"padding:12px 16px 12px 8px;{border}"
            f"color:#111827;font-size:15px;font-weight:{weight};\">{value_html}</td>"
            "</tr>"
        )
    return (
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
        "style=\"border:1px solid #e5e7eb;border-radius:12px;background:#ffffff;\">"
        + "".join(rendered)
        + "</table>"
    )


def _timeline(event, clock):
    steps = _TIMELINES.get(event, _TIMELINES["service_down"])
    cells = []
    for index, (label, tone, active) in enumerate(steps):
        if index:
            cells.append(
                "<td align=\"center\" valign=\"middle\" width=\"6%\" "
                "style=\"color:#cbd5e1;font-size:18px;\">&#8594;</td>"
            )
        background, foreground, symbol = _STEP_TONES[tone]
        when = (
            f"<div style=\"font-size:12px;color:#64748b;margin-top:2px;\">{html.escape(clock)}</div>"
            if active
            else "<div style=\"font-size:12px;line-height:16px;\">&nbsp;</div>"
        )
        cells.append(
            "<td align=\"center\" valign=\"top\" width=\"20%\" style=\"padding:10px 2px;\">"
            f"<div style=\"width:42px;height:42px;line-height:42px;border-radius:21px;"
            f"background:{background};color:{foreground};font-size:18px;font-weight:700;"
            f"margin:0 auto 6px;\">{symbol}</div>"
            f"<div style=\"font-size:12px;font-weight:700;color:#111827;\">{html.escape(label)}</div>"
            f"{when}</td>"
        )
    return (
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
        "style=\"background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;\">"
        "<tr>" + "".join(cells) + "</tr></table>"
    )


def message_text(event, fields):
    title = EVENT_TITLES[event]
    severity_key = fields.get("severity") or SEVERITY.get(event, "critical")
    theme = _THEMES.get(severity_key, _THEMES["critical"])
    clock = _event_time(fields.get("time"))
    summary = _SUMMARIES.get(event, "")
    rows = _detail_table(
        (
            ("&#9638;", "Target", html.escape(str(fields.get("target") or "—")), True),
            ("&#9881;", "Service", html.escape(str(fields.get("service") or "—")), False),
            ("&#128197;", "Event Time", html.escape(clock), False),
            ("&#8767;", "Event", html.escape(str(fields.get("event") or title)), False),
            ("&#128295;", "Action", html.escape(_action_label(fields.get("action"))), False),
            ("&#9873;", "Final Status", _status_badge(fields.get("status"), severity_key), False),
            ("&#9432;", "Reason", html.escape(str(fields.get("reason") or "—")), False),
        )
    )
    body = (
        "<div style=\"margin:0;padding:0;background:#f3f5f8;\">"
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
        "style=\"background:#f3f5f8;\"><tr><td align=\"center\" style=\"padding:24px 12px;\">"
        "<table role=\"presentation\" width=\"640\" cellpadding=\"0\" cellspacing=\"0\" "
        "style=\"width:640px;max-width:640px;background:#ffffff;border:1px solid #e5e7eb;"
        "border-radius:14px;font-family:Segoe UI,Arial,sans-serif;color:#111827;\">"
        "<tr><td bgcolor=\"#0c2340\" style=\"background:#0c2340;padding:22px 26px;\">"
        "<table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\"><tr>"
        "<td valign=\"middle\" style=\"padding-right:14px;\">"
        "<div style=\"width:46px;height:46px;line-height:46px;border:2px solid #ffffff;"
        "border-radius:10px;color:#ffffff;text-align:center;font-size:20px;\">&#9638;</div>"
        "</td><td valign=\"middle\">"
        "<div style=\"font-size:22px;font-weight:700;color:#ffffff;\">KLTN Infrastructure Monitoring</div>"
        "<div style=\"font-size:13px;color:#dbe4ee;padding-top:3px;\">"
        "Automated Monitoring &amp; Remediation</div>"
        "</td></tr></table></td></tr>"
        "<tr><td style=\"padding:18px 22px 8px;\">"
        f"<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
        f"style=\"background:{theme['banner']};border-radius:12px;\"><tr>"
        f"<td width=\"72\" valign=\"middle\" style=\"padding:16px 8px 16px 16px;\">"
        f"<div style=\"width:46px;height:46px;line-height:46px;border-radius:23px;"
        f"background:{theme['accent']};color:#ffffff;text-align:center;font-size:22px;"
        f"font-weight:700;\">{theme['mark']}</div></td>"
        f"<td valign=\"middle\" style=\"padding:16px 16px 16px 4px;\">"
        f"<div style=\"font-size:26px;font-weight:800;color:{theme['title']};\">{html.escape(title)}</div>"
        f"<div style=\"font-size:14px;color:{theme['title']};padding-top:4px;\">{html.escape(summary)}</div>"
        "</td></tr></table></td></tr>"
        f"<tr><td style=\"padding:8px 22px 12px;\">{rows}</td></tr>"
        f"<tr><td style=\"padding:4px 22px 16px;\">{_timeline(event, clock)}</td></tr>"
        "<tr><td style=\"padding:0 22px 22px;\">"
        "<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
        "style=\"background:#f8fafc;border-radius:10px;\"><tr>"
        "<td style=\"padding:12px 16px;color:#64748b;font-size:13px;line-height:1.5;\">"
        "<span style=\"color:#2563eb;font-weight:700;\">&#9432;</span>&nbsp;"
        "This is an automated notification from the KLTN Infrastructure Monitoring System. "
        "Please do not reply to this email."
        "</td></tr></table></td></tr>"
        "</table></td></tr></table></div>"
    )
    service = str(fields.get("service") or "Service")
    target = str(fields.get("target") or "target")
    subject = f"[KLTN] {theme['subject_mark']} {title} – {service} on {target}"
    return subject, body


def _graph_token(settings):
    import msal

    app = msal.ConfidentialClientApplication(
        settings["client_id"],
        authority=f"https://login.microsoftonline.com/{settings['tenant_id']}",
        client_credential=settings["client_secret"],
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    token = result.get("access_token") if isinstance(result, dict) else None
    if not token:
        code = result.get("error") if isinstance(result, dict) else "token_error"
        raise RuntimeError(f"Graph token was not issued ({code}).")
    return token


def _graph_send(event, fields, settings, recipients):
    subject, body = message_text(event, fields)
    token = _graph_token(settings)
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body},
            "toRecipients": [{"emailAddress": {"address": address}} for address in recipients],
        },
        "saveToSentItems": True,
    }
    response = requests.post(
        f"https://graph.microsoft.com/v1.0/users/{quote(settings['sender'])}/sendMail",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=20,
    )
    if response.status_code != 202:
        code = ""
        try:
            code = str((response.json().get("error") or {}).get("code") or "")
        except ValueError:
            code = ""
        raise RuntimeError(f"Graph sendMail failed ({response.status_code} {code}).".strip())
    return response.status_code


def _smtp_send(event, fields, settings, recipients):
    subject, body = message_text(event, fields)
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings["sender"]
    message["To"] = ", ".join(recipients)
    message.set_content(body, subtype="html")
    with smtplib.SMTP(settings["host"], settings["port"], timeout=20) as smtp:
        smtp.starttls()
        smtp.login(settings["user"], settings["password"])
        smtp.send_message(message)
