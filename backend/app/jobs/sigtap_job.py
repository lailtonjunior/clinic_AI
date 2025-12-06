from app.core.config import settings
from app.services.sigtap_tasks import sync_sigtap_current_competencia


def trigger_sync():
    if not settings.sigtap_job_enabled:
        return None
    # Delegates processing to Celery worker; avoid in-process loops.
    return sync_sigtap_current_competencia.delay()


def schedule():
    # Maintained for compatibility with previous startup hook.
    return trigger_sync()
