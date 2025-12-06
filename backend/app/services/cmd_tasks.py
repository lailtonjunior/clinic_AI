from datetime import datetime

from app.celery_app import celery_app
from app.core.config import settings
from app.database import SessionLocal
from app.services.cmd_service import CmdService


def _process_tenant(tenant_id: int):
    session = SessionLocal()
    try:
        service = CmdService(session)
        competencia = datetime.utcnow().strftime("%Y%m")
        service.enviar_pendentes_por_competencia(tenant_id, competencia)
    finally:
        session.close()


@celery_app.task(name="cmd.processar_tenant")
def processar_cmd_tenant(tenant_id: int):
    if not settings.cmd_job_enabled:
        return None
    return _process_tenant(tenant_id)
