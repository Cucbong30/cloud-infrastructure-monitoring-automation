"""Microsoft Entra ID sign-in. Roles come from the App Role claim, not from an email list."""

import secrets

from flask import current_app
from sqlalchemy import select

from app.extensions import db
from app.models import User

ROLES = ("admin", "operator", "viewer")


def sso_configured():
    config = current_app.config
    return bool(config.get("ENTRA_TENANT_ID") and config.get("ENTRA_CLIENT_ID") and config.get("ENTRA_CLIENT_SECRET"))


def role_from_claims(claims):
    """Highest Entra App Role wins. A token with no role stays Viewer."""
    raw = (claims or {}).get("roles") or []
    if isinstance(raw, str):
        raw = [raw]
    found = {str(item).strip().lower() for item in raw}
    for role in ROLES:
        if role in found:
            return role
    return "viewer"


def claims_identity(claims):
    claims = claims or {}
    oid = str(claims.get("oid") or claims.get("sub") or "").strip()
    email = str(claims.get("preferred_username") or claims.get("email") or claims.get("upn") or "").strip()
    username = email or oid
    if len(username) > 80:
        username = username[:80]
    return oid, email[:255], username


def upsert_user(claims):
    oid, email, username = claims_identity(claims)
    if not oid or not username:
        return None
    role = role_from_claims(claims)
    user = db.session.scalar(select(User).where(User.entra_oid == oid))
    if user is None and email:
        user = db.session.scalar(select(User).where(User.email == email))
    if user is None:
        taken = db.session.scalar(select(User).where(User.username == username))
        if taken is not None and taken.entra_oid not in {None, oid}:
            username = oid[:80]
        elif taken is not None:
            user = taken
    if user is None:
        user = User(username=username, role=role, is_active=True)
        user.set_password(secrets.token_urlsafe(32))
        db.session.add(user)
    user.entra_oid = oid
    user.email = email or user.email
    user.username = username
    user.role = role
    user.is_active = True
    db.session.commit()
    return user


def begin_sign_in():
    import msal

    config = current_app.config
    app = msal.ConfidentialClientApplication(
        config["ENTRA_CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{config['ENTRA_TENANT_ID']}",
        client_credential=config["ENTRA_CLIENT_SECRET"],
    )
    return app.initiate_auth_code_flow(
        scopes=["User.Read"],
        redirect_uri=config["ENTRA_REDIRECT_URI"],
    )


def finish_sign_in(flow, request_args):
    import msal

    config = current_app.config
    app = msal.ConfidentialClientApplication(
        config["ENTRA_CLIENT_ID"],
        authority=f"https://login.microsoftonline.com/{config['ENTRA_TENANT_ID']}",
        client_credential=config["ENTRA_CLIENT_SECRET"],
    )
    result = app.acquire_token_by_auth_code_flow(flow, request_args)
    if not isinstance(result, dict) or result.get("error"):
        return None, result.get("error_description") if isinstance(result, dict) else "Microsoft sign-in failed."
    claims = result.get("id_token_claims") or {}
    return claims, None
