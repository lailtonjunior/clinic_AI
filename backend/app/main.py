import asyncio
import logging
import time
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.auth import decode_token
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.routes import core as core_routes
from app.api.routes import sigtap as sigtap_routes
from app.api.routes import auth as auth_routes
from app.api.routes import users as users_routes
from app.api.routes import tenants as tenants_routes
from app.api.routes import cmd as cmd_routes
from app.api.routes import auditoria as auditoria_routes
from app.api.routes import exports as exports_routes
from app.api.routes import ai as ai_routes
from app.jobs import sigtap_job
from app.jobs import cmd_job
from app.scripts import seed_initial_admin

setup_logging()
logger = logging.getLogger("app.request")

app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(core_routes.router, prefix="/api")
app.include_router(sigtap_routes.router, prefix="/api")
app.include_router(auth_routes.router, prefix="/api")
app.include_router(users_routes.router, prefix="/api")
app.include_router(tenants_routes.router, prefix="/api")
app.include_router(cmd_routes.router, prefix="/api")
app.include_router(auditoria_routes.router, prefix="/api")
app.include_router(exports_routes.router, prefix="/api")
app.include_router(ai_routes.router, prefix="/api")

Instrumentator().instrument(app).expose(app, include_in_schema=False)


def _extract_auth_context(request: Request) -> tuple[Optional[int], Optional[int]]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.lower().startswith("bearer "):
        return None, None
    token = auth_header.split(" ", 1)[1]
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub", 0)) if payload.get("sub") else None
        tenant_id = int(payload.get("tenant_id", 0)) if payload.get("tenant_id") else None
        return tenant_id, user_id
    except Exception:
        return None, None


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    tenant_id, user_id = _extract_auth_context(request)
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "request",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": round(duration_ms, 2),
                "tenant_id": tenant_id,
                "user_id": user_id,
            },
        )


@app.on_event("startup")
async def startup_events():
    # Roda sincronizacao mensal do SIGTAP em background
    sigtap_job.schedule()
    cmd_job.schedule()
    if settings.seed_run_on_startup:
        await asyncio.to_thread(seed_initial_admin.run_seed)


@app.get("/health")
def health():
    return {"status": "ok"}
