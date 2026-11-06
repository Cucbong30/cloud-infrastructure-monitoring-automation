from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import select

from app.extensions import db
from app.forms import LoginForm
from app.models import User, utcnow
from app.services.audit import record
from app.services.entra import begin_sign_in, finish_sign_in, sso_configured, upsert_user

bp = Blueprint("auth", __name__)


def safe_next(target):
    if not target or not target.startswith("/") or target.startswith("//") or "\\" in target:
        return url_for("dashboard.index")
    return target


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(select(User).where(User.username == form.username.data.strip()))
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password.", "danger")
        elif not user.is_active:
            flash("Account is inactive.", "danger")
        else:
            user.last_login_at = utcnow()
            db.session.commit()
            login_user(user)
            record("auth.login", "user", user.id, {})
            return redirect(safe_next(request.args.get("next")))
    return render_template("login.html", form=form, sso_enabled=sso_configured())


@bp.get("/auth/microsoft")
def microsoft():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    if not sso_configured():
        flash("Microsoft sign-in is not configured.", "warning")
        return redirect(url_for("auth.login"))
    try:
        flow = begin_sign_in()
    except Exception:
        flash("Microsoft sign-in could not be started.", "danger")
        return redirect(url_for("auth.login"))
    session["entra_flow"] = flow
    session["entra_next"] = safe_next(request.args.get("next"))
    return redirect(flow["auth_uri"])


@bp.get("/auth/callback")
def callback():
    flow = session.pop("entra_flow", None)
    target = session.pop("entra_next", None) or url_for("dashboard.index")
    if not flow or not sso_configured():
        flash("Microsoft sign-in expired. Start again.", "warning")
        return redirect(url_for("auth.login"))
    try:
        claims, error = finish_sign_in(flow, request.args)
    except Exception:
        claims, error = None, "Microsoft sign-in failed."
    if error or not claims:
        flash("Microsoft sign-in was rejected.", "danger")
        return redirect(url_for("auth.login"))
    user = upsert_user(claims)
    if user is None or not user.is_active:
        flash("This Microsoft account cannot sign in.", "danger")
        return redirect(url_for("auth.login"))
    user.last_login_at = utcnow()
    db.session.commit()
    login_user(user)
    record(
        "auth.login",
        "user",
        user.id,
        {"actor": user.username, "role": user.role, "trigger": "manual", "result": "SUCCESS", "message": "Microsoft SSO"},
    )
    return redirect(target)


@bp.post("/logout")
def logout():
    user_id = current_user.id if current_user.is_authenticated else None
    logout_user()
    if user_id is not None:
        record("auth.logout", "user", user_id, {}, user_id=user_id)
    return redirect(url_for("auth.login"))
