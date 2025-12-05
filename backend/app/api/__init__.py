from fastapi import APIRouter
from app.api.routes import core

api_router = APIRouter()
api_router.include_router(core.router)
