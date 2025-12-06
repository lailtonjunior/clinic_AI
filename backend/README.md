# Backend

## Jobs e Celery
- Os jobs de longa duração (SIGTAP e CMD) agora são executados como tasks Celery usando Redis como broker/backend.
- Para rodar localmente, ative o ambiente (venv) e suba um worker:  
  `celery -A app.celery_app worker --loglevel=info`
- No docker-compose, há um serviço `celery-worker` que já usa o mesmo container do backend com o comando acima.
- As tasks são disparadas pelo backend (startup) respeitando as flags `SIGTAP_JOB_ENABLED` e `CMD_JOB_ENABLED` no `.env`.
