from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.config import settings
from app.services.sigtap_sync import SIGTAPSyncService, TabelaSIGTAPRepository
from app.services import audit_log_service
from app.dependencies import get_current_user, get_current_tenant_id, require_roles
from app.models.entities import Role

router = APIRouter(prefix="/sigtap", tags=["sigtap"])


def _require_admin(x_admin_token: str = Header(None, alias="X-Admin-Token")):
    expected = settings.sigtap_admin_token
    if expected and x_admin_token != expected:
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador SIGTAP")
    return True


@router.post("/sync")
def trigger_sync(
    competencia: str = Query(..., min_length=6, max_length=6, regex="^\\d{6}$"),
    db: Session = Depends(get_db_session),
    _: bool = Depends(_require_admin),
    current_user=Depends(require_roles(Role.ADMIN_TENANT.value, Role.SUPER_ADMIN.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    repo = TabelaSIGTAPRepository(db)
    service = SIGTAPSyncService(repo)
    try:
        result = service.sync(competencia)
        audit_log_service.log_action(db, current_tenant_id, current_user.id, "SYNC_SIGTAP", "SIGTAP", competencia, {"result": result})
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/status")
def sigtap_status(
    db: Session = Depends(get_db_session),
    _: bool = Depends(_require_admin),
    __=Depends(require_roles(Role.ADMIN_TENANT.value, Role.SUPER_ADMIN.value)),
):
    repo = TabelaSIGTAPRepository(db)
    ultima = repo.ultima_competencia()
    return {
        "ultima_competencia": ultima,
        "total_registros": repo.total_registros(),
    }
