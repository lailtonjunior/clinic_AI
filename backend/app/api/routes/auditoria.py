from collections import Counter
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.dependencies import get_current_tenant_id, require_roles

router = APIRouter()


@router.get("/auditoria/competencia/{competencia}")
def auditoria_competencia(
    competencia: str,
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
    _: models.Usuario = Depends(
        require_roles(
            models.Role.FATURAMENTO.value,
            models.Role.ADMIN_TENANT.value,
            models.Role.AUDITOR_INTERNO.value,
        )
    ),
):
    procedimentos: List[models.ProcedimentoSUS] = db.scalars(
        select(models.ProcedimentoSUS).where(
            models.ProcedimentoSUS.competencia_aaaamm == competencia,
            models.ProcedimentoSUS.tenant_id == current_tenant_id,
        )
    ).all()

    atendimento_ids = [p.atendimento_id for p in procedimentos]
    atendimentos = (
        {a.id: a for a in db.scalars(select(models.Atendimento).where(models.Atendimento.id.in_(atendimento_ids))).all()}
        if atendimento_ids
        else {}
    )
    paciente_ids = [a.paciente_id for a in atendimentos.values()]
    pacientes = (
        {p.id: p for p in db.scalars(select(models.Paciente).where(models.Paciente.id.in_(paciente_ids))).all()}
        if paciente_ids
        else {}
    )

    total = len(procedimentos)
    total_com_erros = 0
    counter = Counter()
    exemplos = []

    for proc in procedimentos:
        resultado = proc.validacoes_json or {}
        erros = resultado.get("erros") or []
        if resultado.get("ok") is False and not erros:
            # Guarda estado inconsistente, mas sem lista de erros.
            erros = ["validacao_falhou_sem_erros"]
        if erros:
            total_com_erros += 1
            counter.update(erros)
            if len(exemplos) < 5:
                atendimento = atendimentos.get(proc.atendimento_id)
                paciente = pacientes.get(atendimento.paciente_id) if atendimento else None
                exemplos.append(
                    {
                        "id": proc.id,
                        "paciente": paciente.nome if paciente else None,
                        "procedimento": proc.sigtap_codigo,
                        "mensagens": erros,
                    }
                )

    erros_agrupados = [{"tipo": err, "quantidade": count} for err, count in counter.most_common()]

    return {
        "competencia": competencia,
        "total_procedimentos": total,
        "total_com_erros": total_com_erros,
        "erros_agrupados": erros_agrupados,
        "exemplos_com_erros": exemplos,
    }
