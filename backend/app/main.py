import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import core as core_routes
from app.api.routes import sigtap as sigtap_routes
from app.api.routes import auth as auth_routes
from app.api.routes import users as users_routes
from app.api.routes import tenants as tenants_routes
from app.api.routes import cmd as cmd_routes
from app.jobs import sigtap_job
from app.jobs import cmd_job
from app.scripts import seed_initial_admin

app = FastAPI(title=settings.app_name, version="0.1.0")

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
