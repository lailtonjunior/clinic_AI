from datetime import datetime
from typing import Optional

from app.celery_app import celery_app
from app.core.config import settings
from app.database import SessionLocal
from app.services.sigtap_sync import SIGTAPSyncService, TabelaSIGTAPRepository


def _sync_current_competencia() -> Optional[dict]:
    competencia_atual = datetime.utcnow().strftime("%Y%m")
    session = SessionLocal()
    repo = TabelaSIGTAPRepository(session)
    try:
        if repo.competencia_importada(competencia_atual):
            return None
        service = SIGTAPSyncService(repo)
        return service.sync(competencia_atual)
    finally:
        session.close()


@celery_app.task(name="sigtap.sync_current_competencia")
def sync_sigtap_current_competencia():
    if not settings.sigtap_job_enabled:
        return None
    return _sync_current_competencia()
