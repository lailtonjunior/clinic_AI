from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.core.config import settings
from app.dependencies import get_current_tenant_id, get_current_user
from app.services.ai_assistant import AiAssistantService

router = APIRouter(prefix="/ai", tags=["ai"])


class AssistenteRequest(BaseModel):
    mensagem: str
    paciente_id: Optional[int] = None
    atendimento_id: Optional[int] = None


def _idade(data_nascimento: date, ref: date) -> int:
    anos = ref.year - data_nascimento.year
    if (ref.month, ref.day) < (data_nascimento.month, data_nascimento.day):
        anos -= 1
    return anos


@router.post("/assistente")
def assistente_clinico(
    payload: AssistenteRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(get_current_user),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    if not settings.ai_api_key or not settings.ai_model_name:
        raise HTTPException(status_code=503, detail="Assistente AI não configurado")

    paciente = db.get(models.Paciente, payload.paciente_id) if payload.paciente_id else None
    atendimento = db.get(models.Atendimento, payload.atendimento_id) if payload.atendimento_id else None
    if atendimento and atendimento.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Atendimento de outro tenant")
    if paciente and paciente.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Paciente de outro tenant")

    if atendimento and not paciente:
        paciente = db.get(models.Paciente, atendimento.paciente_id)

    procedimentos = []
    if atendimento:
        procedimentos = db.scalars(
            select(models.ProcedimentoSUS).where(
                models.ProcedimentoSUS.atendimento_id == atendimento.id,
                models.ProcedimentoSUS.tenant_id == current_tenant_id,
            )
        ).all()

    contexto = {
        "usuario": {"id": current_user.id, "nome": current_user.nome},
        "paciente": None,
        "atendimento": None,
        "procedimentos": [],
    }
    if paciente:
        ref_date = atendimento.data.date() if atendimento and isinstance(atendimento.data, datetime) else date.today()
        contexto["paciente"] = {
            "id": paciente.id,
            "nome": paciente.nome,
            "sexo": paciente.sexo,
            "idade": _idade(paciente.data_nascimento, ref_date),
            "cid_principal": (paciente.cid_deficiencia or ""),
        }
    if atendimento:
        contexto["atendimento"] = {
            "id": atendimento.id,
            "data": atendimento.data.isoformat(),
            "tipo": atendimento.tipo,
        }
    if procedimentos:
        contexto["procedimentos"] = [
            {"codigo": p.sigtap_codigo, "cid": p.cid10, "quantidade": p.quantidade} for p in procedimentos
        ]

    service = AiAssistantService()
    resposta = service.gerar_resposta(contexto, payload.mensagem)
    return {"resposta": resposta}
