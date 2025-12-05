from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.dependencies import get_current_tenant_id, get_current_user, get_current_roles, require_roles
from app.services.cmd_service import CmdService

router = APIRouter(prefix="/cmd", tags=["cmd"])


@router.post("/contatos/sincronizar")
def sincronizar_cmd(
    competencia: str,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.FATURAMENTO.value, models.Role.SUPER_ADMIN.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
    roles: list[str] = Depends(get_current_roles),
    tenant_id: Optional[int] = None,
):
    if tenant_id and models.Role.SUPER_ADMIN.value not in roles:
        raise HTTPException(status_code=403, detail="Acesso a outro tenant nao permitido")
    target_tenant = tenant_id or current_tenant_id
    service = CmdService(db)
    enviados = service.enviar_pendentes_por_competencia(target_tenant, competencia)
    return {"enviados": [c.id for c in enviados]}


@router.post("/contatos/{contato_id}/reenvio")
def reenviar_contato(
    contato_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.FATURAMENTO.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    service = CmdService(db)
    contato = service.enviar_contato(current_tenant_id, contato_id)
    return {"id": contato.id, "status": contato.status_envio_cmd, "erro": contato.ultimo_erro_cmd}


@router.post("/contatos/{contato_id}/cancelar")
def cancelar_contato(
    contato_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.FATURAMENTO.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    service = CmdService(db)
    contato = service.cancelar_contato(current_tenant_id, contato_id)
    return {"id": contato.id, "status": contato.status_envio_cmd, "erro": contato.ultimo_erro_cmd}


@router.get("/contatos/{contato_id}")
def obter_contato(
    contato_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.FATURAMENTO.value, models.Role.AUDITOR_INTERNO.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    contato = db.get(models.CmdContato, contato_id)
    if not contato or contato.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Contato CMD nao encontrado")
    return {
        "id": contato.id,
        "uuid": contato.codigo_cmd_uuid,
        "status": contato.status_envio_cmd,
        "erro": contato.ultimo_erro_cmd,
        "competencia": contato.competencia,
    }
