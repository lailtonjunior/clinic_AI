from sqlalchemy import select

from app import models
from app.core.config import settings
from app.database import SessionLocal
from app.services.cmd_tasks import processar_cmd_tenant


def trigger_for_active_tenants():
    if not settings.cmd_job_enabled:
        return None
    session = SessionLocal()
    try:
        ativos = session.scalars(select(models.CmdConfigTenant).where(models.CmdConfigTenant.ativo.is_(True))).all()
        results = []
        for cfg in ativos:
            results.append(processar_cmd_tenant.delay(cfg.tenant_id))
        return results
    finally:
        session.close()


def schedule():
    # Maintained for compatibility with previous startup hook.
    return trigger_for_active_tenants()
