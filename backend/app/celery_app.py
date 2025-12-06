from celery import Celery

from app.core.config import settings

# Celery application configured to use Redis for broker/result backend.
celery_app = Celery(
    "clinic_ai",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.services.sigtap_tasks",
        "app.services.cmd_tasks",
    ],
)

celery_app.autodiscover_tasks(["app"])

__all__ = ("celery_app",)
