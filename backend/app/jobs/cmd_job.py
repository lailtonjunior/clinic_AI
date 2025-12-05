import asyncio
from typing import Optional

from sqlalchemy import select

from app.core.config import settings
from app.database import SessionLocal
from app import models
from app.services.cmd_service import CmdService


def _process_tenant(tenant_id: int):
    session = SessionLocal()
    try:
        service = CmdService(session)
        # Envia apenas competencia corrente (AAAAMM)
        from datetime import datetime

        competencia = datetime.utcnow().strftime("%Y%m")
        service.enviar_pendentes_por_competencia(tenant_id, competencia)
    finally:
        session.close()


async def run_cmd_job():
    while True:
        if settings.cmd_job_enabled:
            session = SessionLocal()
            try:
                ativos = session.scalars(select(models.CmdConfigTenant).where(models.CmdConfigTenant.ativo.is_(True))).all()
                for cfg in ativos:
                    await asyncio.to_thread(_process_tenant, cfg.tenant_id)
            finally:
                session.close()
        await asyncio.sleep(max(1, settings.cmd_job_interval_minutes) * 60)


def schedule():
    if not settings.cmd_job_enabled:
        return None
    return asyncio.create_task(run_cmd_job())
