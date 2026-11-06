from flask import Blueprint, render_template
from sqlalchemy import select

from app.authz import roles_required
from app.extensions import db
from app.models import User

bp = Blueprint("users", __name__, url_prefix="/users")


@bp.get("/")
@roles_required("admin")
def index():
    users = db.session.scalars(select(User).order_by(User.username)).all()
    return render_template("users/list.html", users=users)
