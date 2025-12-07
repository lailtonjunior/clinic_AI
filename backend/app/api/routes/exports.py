from datetime import datetime
from pathlib import Path
from typing import Literal, Optional, List, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.dependencies import get_current_tenant_id, require_roles
from app.models.entities import Role
from app.services import audit_log_service, export_bpa, export_apac, minio_service, sigtap_rules

router = APIRouter(prefix="/exports", tags=["exports"])


def _garante_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def _coletar_procedimentos_bpa(
    competencia: str,
    tenant_id: int,
    db: Session,
    unidade_id: int | None = None,
    profissional_id: int | None = None,
) -> List[Dict[str, str]]:
    stmt = select(models.ProcedimentoSUS).where(
        models.ProcedimentoSUS.competencia_aaaamm == competencia,
        models.ProcedimentoSUS.tenant_id == tenant_id,
    )
    procedimentos = db.scalars(stmt).all()
    linhas: List[Dict[str, str]] = []
    for proc in procedimentos:
        atendimento = db.get(models.Atendimento, proc.atendimento_id)
        if not atendimento:
            continue
        if unidade_id and atendimento.unidade_id != unidade_id:
            continue
        if profissional_id and atendimento.profissional_id != profissional_id:
            continue
        paciente = db.get(models.Paciente, atendimento.paciente_id)
        profissional = db.get(models.Profissional, atendimento.profissional_id)
        unidade = db.get(models.Unidade, atendimento.unidade_id)
        if not paciente or not profissional or not unidade:
            continue
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        doc = sigtap_rules.decide_documento_bpa(paciente, tabela)
        valor_procedimento = 0
        if proc.valores and proc.valores.get("valor") is not None:
            valor_procedimento = proc.valores.get("valor")
        elif tabela and tabela.valor is not None:
            valor_procedimento = float(tabela.valor)
        linhas.append({
            "cnes": unidade.cnes,
            "competencia": proc.competencia_aaaamm,
            "cns_prof": profissional.cns,
            "cbo": proc.profissional_cbo,
            "data_atendimento": atendimento.data.strftime("%Y%m%d"),
            "procedimento": proc.sigtap_codigo,
            "cns_paciente": paciente.cns if doc == "CNS" else "",
            "cpf_paciente": paciente.cpf if doc == "CPF" else "",
            "sexo": paciente.sexo,
            "cid": proc.cid10,
            "idade": sigtap_rules.calcular_idade(paciente.data_nascimento, atendimento.data.date()),
            "quantidade": proc.quantidade,
            "valor": valor_procedimento,
        })
    return linhas


def _generate_bpa(
    competencia: str,
    tenant_id: int,
    db: Session,
    unidade_id: int | None = None,
    profissional_id: int | None = None,
) -> tuple[str, str]:
    procedimentos = _coletar_procedimentos_bpa(competencia, tenant_id, db, unidade_id=unidade_id, profissional_id=profissional_id)
    if not procedimentos:
        raise HTTPException(status_code=400, detail="Nenhum procedimento encontrado para a competencia")

    conteudo = export_bpa.gerar_arquivo(
        competencia=competencia,
        orgao="CER",
        sigla="CER",
        cnpj="00000000000000",
        destino="M",
        versao="0.1.0",
        procedimentos=procedimentos,
    )
    destino_path = Path("exports/bpa") / f"bpa_{competencia}.rem"
    _garante_dir(destino_path)
    destino_path.write_text(conteudo, encoding="utf-8")
    uploaded_key = minio_service.upload_bytes(f"exports/bpa/bpa_{competencia}.rem", conteudo.encode("ascii", errors="ignore"))
    presigned = minio_service.presign_get(uploaded_key) if uploaded_key else None
    return conteudo, presigned or str(destino_path)


def _coletar_procedimentos_apac(
    competencia: str,
    tenant_id: int,
    db: Session,
    unidade_id: int | None = None,
    profissional_id: int | None = None,
) -> List[models.ProcedimentoSUS]:
    stmt = select(models.ProcedimentoSUS).where(
        models.ProcedimentoSUS.competencia_aaaamm == competencia,
        models.ProcedimentoSUS.tenant_id == tenant_id,
    )
    procedimentos = db.scalars(stmt).all()
    filtrados: List[models.ProcedimentoSUS] = []
    for proc in procedimentos:
        atendimento = db.get(models.Atendimento, proc.atendimento_id)
        if not atendimento:
            continue
        if unidade_id and atendimento.unidade_id != unidade_id:
            continue
        if profissional_id and atendimento.profissional_id != profissional_id:
            continue
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        if tabela and tabela.exige_apac:
            filtrados.append(proc)
    return filtrados


def _generate_apac(
    competencia: str,
    tenant_id: int,
    db: Session,
    unidade_id: int | None = None,
    profissional_id: int | None = None,
) -> tuple[str, str]:
    procedimentos_apac = _coletar_procedimentos_apac(
        competencia, tenant_id, db, unidade_id=unidade_id, profissional_id=profissional_id
    )
    if not procedimentos_apac:
        raise HTTPException(status_code=400, detail="Nenhum procedimento exige APAC nesta competencia")
    proc = procedimentos_apac[0]
    atendimento = db.get(models.Atendimento, proc.atendimento_id)
    paciente = db.get(models.Paciente, atendimento.paciente_id)
    profissional = db.get(models.Profissional, atendimento.profissional_id)
    unidade = db.get(models.Unidade, atendimento.unidade_id)
    numero_apac = str(proc.id).zfill(13)
    corpo = {
        "competencia": competencia,
        "numero_apac": numero_apac,
        "uf": unidade.uf,
        "cnes": unidade.cnes,
        "data_autorizacao": atendimento.data.strftime("%Y%m%d"),
        "data_validade": atendimento.data.strftime("%Y%m%d"),
        "tipo_atendimento": "01",
        "tipo_apac": "01",
        "cns_paciente": paciente.cns,
        "nome_paciente": paciente.nome,
        "nome_mae": paciente.nome_mae or "",
        "logradouro": (paciente.contato or {}).get("logradouro", "logradouro"),
        "numero_endereco": str((paciente.contato or {}).get("numero", "0")),
        "complemento": (paciente.contato or {}).get("complemento", ""),
        "cep": str((paciente.contato or {}).get("cep", "0")),
        "municipio_ibge": unidade.ibge_cod,
        "data_nascimento": paciente.data_nascimento.strftime("%Y%m%d"),
        "sexo": paciente.sexo,
        "nome_medico_responsavel": profissional.nome,
        "procedimento_principal": proc.sigtap_codigo,
        "motivo_saida": "01",
        "data_obito_alta": "",
        "nome_autorizador": profissional.nome,
        "cns_medico_resp": profissional.cns,
        "cns_autorizador": profissional.cns,
        "cid_associado": proc.cid10,
        "num_prontuario": str(atendimento.id).zfill(10),
        "cnes_solicitante": unidade.cnes,
        "data_solicitacao": atendimento.data.strftime("%Y%m%d"),
        "data_autorizacao": atendimento.data.strftime("%Y%m%d"),
        "codigo_emissor": proc.sigtap_codigo,
        "carater_atendimento": "01",
        "apac_anterior": "",
        "raca_cor": (paciente.contato or {}).get("raca_cor", "99"),
        "nome_responsavel": paciente.nome_mae or paciente.nome,
        "nacionalidade": (paciente.contato or {}).get("nacionalidade", "010"),
        "etnia": (paciente.contato or {}).get("etnia", "") if (paciente.contato or {}).get("raca_cor") == "05" else "",
        "cod_logradouro_ibge": (paciente.contato or {}).get("tipo_logradouro", "001"),
        "bairro": (paciente.contato or {}).get("bairro", "bairro"),
        "ddd": (paciente.contato or {}).get("ddd", ""),
        "fone": (paciente.contato or {}).get("fone", ""),
        "email": (paciente.contato or {}).get("email", ""),
        "cns_executor": profissional.cns,
        "cpf_paciente": paciente.cpf or "",
        "ine": unidade.ibge_cod,
        "pessoa_rua": (paciente.contato or {}).get("pessoa_rua", ""),
        "fonte_orc": "",
        "emenda": "",
        "fim": "  ",
        "data_processamento": atendimento.data.strftime("%Y%m%d"),
        "data_inicio_validade": atendimento.data.strftime("%Y%m%d"),
        "data_fim_validade": atendimento.data.strftime("%Y%m%d"),
        "tipo_atendimento": "01",
        "tipo_apac": "1",
    }
    procs = []
    for proc in procedimentos_apac:
        procs.append({
            "competencia": competencia,
            "numero_apac": numero_apac,
            "codigo": proc.sigtap_codigo,
            "quantidade": proc.quantidade,
            "cbo": proc.profissional_cbo,
        })
    conteudo = export_apac.gerar_arquivo(
        competencia=competencia,
        orgao="CER",
        sigla="CER",
        cnpj="00000000000000",
        destino="SES",
        versao="0.1.0",
        corpo=corpo,
        procedimentos=procs,
    )
    destino_path = Path("exports/apac") / f"apac_{competencia}.rem"
    _garante_dir(destino_path)
    destino_path.write_text(conteudo, encoding="utf-8")
    uploaded_key = minio_service.upload_bytes(f"exports/apac/apac_{competencia}.rem", conteudo.encode("ascii", errors="ignore"))
    presigned = minio_service.presign_get(uploaded_key) if uploaded_key else None
    return conteudo, presigned or str(destino_path)


@router.get("")
def list_exports(
    tipo: Literal["bpa", "apac"],
    competencia: Optional[str] = Query(None, min_length=6, max_length=6),
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
    _: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value, Role.SUPER_ADMIN.value)),
):
    model = models.ExportacaoBPA if tipo == "bpa" else models.ExportacaoAPAC
    stmt = select(model).where(model.tenant_id == current_tenant_id)
    if competencia:
        stmt = stmt.where(model.competencia == competencia)
    stmt = stmt.order_by(model.id.desc())
    exports = db.scalars(stmt).all()
    return exports


@router.post("/{tipo}/{export_id}/retry")
def retry_export(
    tipo: Literal["bpa", "apac"],
    export_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    model = models.ExportacaoBPA if tipo == "bpa" else models.ExportacaoAPAC
    exp = db.get(model, export_id)
    if not exp or exp.tenant_id != current_tenant_id:
        raise HTTPException(status_code=404, detail="Exportacao nao encontrada")

    competencia = exp.competencia
    try:
        conteudo, path = _generate_bpa(competencia, current_tenant_id, db) if tipo == "bpa" else _generate_apac(competencia, current_tenant_id, db)
        exp.arquivo_path = path
        exp.status = "gerado"
        exp.erros_json = {}
        exp.checksum = ""  # manter compatível com pipeline atual
        db.add(exp)
        db.commit()
        audit_log_service.log_action(db, current_tenant_id, current_user.id, "RETRY_EXPORT", model.__name__, exp.id)
    except HTTPException:
        raise
    except Exception as exc:
        exp.status = "erro"
        exp.erros_json = {"message": str(exc)}
        db.add(exp)
        db.commit()
        raise HTTPException(status_code=500, detail="Falha ao reprocessar exportacao")

    return exp
