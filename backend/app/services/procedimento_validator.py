from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app import models
from app.services import sigtap_rules


class ProcedimentoValidatorService:
    def __init__(self, db: Session):
        self.db = db

    def _get_context(self, procedimento: models.ProcedimentoSUS):
        atendimento = self.db.get(models.Atendimento, procedimento.atendimento_id)
        paciente = self.db.get(models.Paciente, atendimento.paciente_id) if atendimento else None
        profissional = self.db.get(models.Profissional, atendimento.profissional_id) if atendimento else None
        unidade = self.db.get(models.Unidade, atendimento.unidade_id) if atendimento else None
        data_atendimento = (
            atendimento.data.date() if atendimento and isinstance(atendimento.data, datetime) else atendimento.data if atendimento else None
        )
        return atendimento, paciente, profissional, unidade, data_atendimento

    def validar_procedimento(self, procedimento: models.ProcedimentoSUS) -> Dict[str, Any]:
        erros: List[str] = []
        avisos: List[str] = []

        atendimento, paciente, profissional, unidade, data_atendimento = self._get_context(procedimento)
        if not atendimento or not paciente or not profissional or not unidade:
            erros.append("contexto_atendimento_incompleto")
            return {"ok": False, "erros": erros, "avisos": avisos}

        tabela_proc = sigtap_rules.get_tabela_para_competencia(
            self.db, procedimento.sigtap_codigo, procedimento.competencia_aaaamm
        )
        erros.extend(
            sigtap_rules.validate_procedimento(
                self.db,
                paciente,
                procedimento,
                unidade,
                profissional,
                data_atendimento,
                tabela_proc=tabela_proc,
            )
        )

        return {"ok": len(erros) == 0, "erros": erros, "avisos": avisos}
