"""Keep lab labels and AZURE01 on the inventory without resetting live status."""

from sqlalchemy import select

from app.extensions import db
from app.models import Server, utcnow
from app.services.inventory import LAB_TARGETS, refresh_cloud_target

_LOCAL = ("WEB01", "APP01", "WIN01", "MON01")


def sync_inventory():
    refresh_cloud_target()
    for name in _LOCAL:
        server = db.session.scalar(select(Server).where(Server.name == name))
        if server is None:
            continue
        if server.environment in {"prod", "staging", "local"}:
            server.environment = "local"
        server.provider = "vmware"
    spec = LAB_TARGETS["AZURE01"]
    server = db.session.scalar(select(Server).where(Server.name == "AZURE01"))
    if server is None:
        server = Server(name="AZURE01", status="unknown", is_active=True, created_at=utcnow())
        db.session.add(server)
    server.hostname = spec["hostname"]
    server.ip_address = spec["ip_address"]
    server.environment = "cloud"
    server.provider = "azure"
    server.os_type = "linux"
    server.monitoring_target = spec["monitoring_target"]
    server.automation_group = spec["automation_group"]
    server.is_active = True
    server.updated_at = utcnow()
    db.session.commit()
