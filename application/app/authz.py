from functools import wraps

from flask import abort, redirect, request, url_for
from flask_login import current_user


def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login", next=request.path))
            if current_user.role not in roles:
                if request.endpoint in {"automation.create_job", "automation.retry", "alerts.remediate"}:
                    try:
                        from app.services.audit import record

                        record(
                            "permission.denied",
                            "automation_job",
                            None,
                            {
                                "result": "DENIED",
                                "message": f"Permission denied for {current_user.role.capitalize()} role",
                                "mode": "MANUAL",
                                "trigger": "manual",
                                "action": request.form.get("action_key") or "—",
                                "target": request.form.get("server_id") or "—",
                            },
                            user_id=current_user.id,
                        )
                    except Exception:
                        pass
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
