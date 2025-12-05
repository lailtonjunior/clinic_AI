"""
Regras de validacao de procedimentos SIGTAP (anti-glosa).
"""
from datetime import date
from typing import List, Optional

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import models
from app.services.validators import validate_cns, validate_cnes, validate_sigtap_codigo


def calcular_idade(data_nascimento: date, data_referencia: date) -> int:
    if not data_nascimento or not data_referencia:
        return 0
    anos = data_referencia.year - data_nascimento.year
    if (data_referencia.month, data_referencia.day) < (data_nascimento.month, data_nascimento.day):
        anos -= 1
    return anos


def get_tabela_para_competencia(db: Session, codigo: str, competencia: str) -> Optional[models.TabelaSIGTAP]:
    """
    Retorna a tabela vigente para o procedimento e competencia informados.
    """
    stmt = (
        select(models.TabelaSIGTAP)
        .where(models.TabelaSIGTAP.codigo == codigo)
        .where(or_(models.TabelaSIGTAP.vigencia_inicio.is_(None), models.TabelaSIGTAP.vigencia_inicio <= competencia))
        .where(or_(models.TabelaSIGTAP.vigencia_fim.is_(None), models.TabelaSIGTAP.vigencia_fim >= competencia))
        .order_by(models.TabelaSIGTAP.vigencia_inicio.desc(), models.TabelaSIGTAP.id.desc())
    )
    return db.scalars(stmt).first()


def existe_procedimento(db: Session, codigo: str) -> bool:
    stmt = select(models.TabelaSIGTAP).where(models.TabelaSIGTAP.codigo == codigo)
    return db.scalars(stmt).first() is not None


def validate_procedimento(
    db: Session,
    paciente,
    proc_model,
    unidade,
    profissional,
    data_atendimento: date,
    tabela_proc: Optional[models.TabelaSIGTAP] = None,
) -> List[str]:
    """
    Retorna lista de erros de validacao do procedimento para a competencia/data informada.
    """
    erros: List[str] = []
    tabela_proc = tabela_proc or get_tabela_para_competencia(db, proc_model.sigtap_codigo, proc_model.competencia_aaaamm)
    if not tabela_proc:
        codigo_existe = existe_procedimento(db, proc_model.sigtap_codigo)
        erros.append("procedimento_fora_vigencia" if codigo_existe else "procedimento_nao_encontrado_sigtap")
    else:
        if tabela_proc.exige_cid and not getattr(proc_model, "cid10", None):
            erros.append("cid_obrigatorio_faltando")
        idade = calcular_idade(paciente.data_nascimento, data_atendimento)
        if tabela_proc.idade_min is not None and idade < tabela_proc.idade_min:
            erros.append("idade_inferior_limite")
        if tabela_proc.idade_max is not None and idade > tabela_proc.idade_max:
            erros.append("idade_superior_limite")
        if tabela_proc.sexo_permitido in ("M", "F") and tabela_proc.sexo_permitido != paciente.sexo:
            erros.append("sexo_incompativel")
        if tabela_proc.exige_apac:
            erros.append("procedimento_exige_apac")

    doc_rule = tabela_proc.doc_paciente if tabela_proc else "AMBOS_PERMITIDOS"
    if doc_rule == "CNS" and not paciente.cns:
        erros.append("doc_paciente_requer_cns")
    if doc_rule == "CPF" and not paciente.cpf:
        erros.append("doc_paciente_requer_cpf")

    if not validate_cnes(unidade.cnes):
        erros.append("dv_cnes_invalido")
    if not validate_cns(profissional.cns):
        erros.append("dv_cns_prof_invalido")
    if not validate_sigtap_codigo(proc_model.sigtap_codigo):
        erros.append("dv_sigtap_invalido")

    return erros


def decide_documento_bpa(paciente, tabela_proc) -> str:
    """
    Decide CNS ou CPF a ser usado na linha BPA conforme regra do procedimento.
    """
    regra = tabela_proc.doc_paciente if tabela_proc else "AMBOS_PERMITIDOS"
    if regra == "CNS":
        return "CNS"
    if regra == "CPF":
        return "CPF"
    if paciente.cns:
        return "CNS"
    if paciente.cpf:
        return "CPF"
    return "CNS"
