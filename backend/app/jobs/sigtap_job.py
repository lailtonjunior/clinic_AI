import asyncio
from datetime import datetime
from typing import Optional

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


async def run_daily():
    while True:
        try:
            await asyncio.to_thread(_sync_current_competencia)
        except Exception as exc:
            print(f"[sigtap_job] erro ao sincronizar SIGTAP: {exc}")
        await asyncio.sleep(max(1, settings.sigtap_job_interval_hours) * 3600)


def schedule():
    if not settings.sigtap_job_enabled:
        return None
    return asyncio.create_task(run_daily())
