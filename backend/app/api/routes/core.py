from datetime import datetime
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_db_session
from app import models
from app.schemas import base as schemas
from app.services import sigtap_rules
from app.services import export_bpa, export_apac
from app.services import minio_service
from app.services import audit_log_service
from app.dependencies import (
    apply_tenant_filter,
    ensure_same_tenant,
    get_current_tenant_id,
    get_current_user,
    require_roles,
)
from app.models.entities import Role

router = APIRouter()


def _build_download_response(content: str, filename: str) -> StreamingResponse:
    data = content.encode("ascii", errors="ignore")
    return StreamingResponse(
        iter([data]),
        media_type="text/plain; charset=ascii",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(data)),
        },
    )


def _commit_and_refresh(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.post("/tenants", response_model=schemas.Tenant)
def create_tenant(
    payload: schemas.TenantCreate,
    db: Session = Depends(get_db_session),
    _: models.Usuario = Depends(require_roles(Role.SUPER_ADMIN.value)),
):
    tenant = models.Tenant(**payload.model_dump())
    return _commit_and_refresh(db, tenant)


@router.get("/tenants", response_model=List[schemas.Tenant])
def list_tenants(
    db: Session = Depends(get_db_session),
    _: models.Usuario = Depends(require_roles(Role.SUPER_ADMIN.value)),
):
    return db.scalars(select(models.Tenant)).all()


@router.post("/unidades", response_model=schemas.Unidade)
def create_unidade(
    payload: schemas.UnidadeCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.ADMIN_TENANT.value, Role.SUPER_ADMIN.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    unidade = models.Unidade(**data)
    obj = _commit_and_refresh(db, unidade)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_UNIDADE", "Unidade", obj.id)
    return obj


@router.get("/unidades", response_model=List[schemas.Unidade])
def list_unidades(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = apply_tenant_filter(select(models.Unidade), models.Unidade, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/profissionais", response_model=schemas.Profissional)
def create_profissional(
    payload: schemas.ProfissionalCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.ADMIN_TENANT.value, Role.CLINICO.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    data = payload.model_dump()
    if data["tenant_id"] != current_tenant_id:
        data["tenant_id"] = current_tenant_id
    unidade = db.get(models.Unidade, data["unidade_id"])
    if not unidade or unidade.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Unidade de outro tenant")
    prof = models.Profissional(**data)
    obj = _commit_and_refresh(db, prof)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_PROFISSIONAL", "Profissional", obj.id)
    return obj


@router.get("/profissionais", response_model=List[schemas.Profissional])
def list_profissionais(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = apply_tenant_filter(select(models.Profissional), models.Profissional, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/pacientes", response_model=schemas.Paciente)
def create_paciente(
    payload: schemas.PacienteCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.RECEPCAO.value, Role.CLINICO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    if not payload.cns and not payload.cpf:
        raise HTTPException(status_code=400, detail="CPF ou CNS obrigatorio")
    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    pac = models.Paciente(**data)
    obj = _commit_and_refresh(db, pac)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_PACIENTE", "Paciente", obj.id)
    return obj


@router.get("/pacientes", response_model=List[schemas.Paciente])
def list_pacientes(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = apply_tenant_filter(select(models.Paciente), models.Paciente, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/agendas", response_model=schemas.Agenda)
def create_agenda(
    payload: schemas.AgendaCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.RECEPCAO.value, Role.CLINICO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    unidade = db.get(models.Unidade, data["unidade_id"])
    profissional = db.get(models.Profissional, data["profissional_id"])
    paciente = db.get(models.Paciente, data["paciente_id"]) if data.get("paciente_id") else None
    for ent in [unidade, profissional, paciente]:
        if ent and getattr(ent, "tenant_id", current_tenant_id) != current_tenant_id:
            raise HTTPException(status_code=403, detail="Referencia a outro tenant")
    ag = models.Agenda(**data)
    obj = _commit_and_refresh(db, ag)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_AGENDA", "Agenda", obj.id)
    return obj


@router.get("/agendas", response_model=List[schemas.Agenda])
def list_agendas(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = apply_tenant_filter(select(models.Agenda), models.Agenda, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/atendimentos", response_model=schemas.Atendimento)
def create_atendimento(
    payload: schemas.AtendimentoCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.CLINICO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    unidade = db.get(models.Unidade, data["unidade_id"])
    profissional = db.get(models.Profissional, data["profissional_id"])
    paciente = db.get(models.Paciente, data["paciente_id"])
    for ent in [unidade, profissional, paciente]:
        if not ent or getattr(ent, "tenant_id", current_tenant_id) != current_tenant_id:
            raise HTTPException(status_code=403, detail="Referencia a outro tenant")
    at = models.Atendimento(**data)
    obj = _commit_and_refresh(db, at)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_ATENDIMENTO", "Atendimento", obj.id)
    return obj


@router.get("/atendimentos", response_model=List[schemas.Atendimento])
def list_atendimentos(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = apply_tenant_filter(select(models.Atendimento), models.Atendimento, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/evolucoes", response_model=schemas.Evolucao)
def create_evolucao(
    payload: schemas.EvolucaoCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.CLINICO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    atendimento = db.get(models.Atendimento, data["atendimento_id"])
    if not atendimento or atendimento.tenant_id != current_tenant_id:
        raise HTTPException(status_code=403, detail="Atendimento de outro tenant")
    evo = models.EvolucaoProntuario(**data)
    obj = _commit_and_refresh(db, evo)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_EVOLUCAO", "EvolucaoProntuario", obj.id)
    return obj


@router.get("/evolucoes", response_model=List[schemas.Evolucao])
def list_evolucoes(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
    _: models.Usuario = Depends(require_roles(Role.CLINICO.value, Role.ADMIN_TENANT.value, Role.AUDITOR_INTERNO.value)),
):
    stmt = apply_tenant_filter(select(models.EvolucaoProntuario), models.EvolucaoProntuario, current_tenant_id)
    return db.scalars(stmt).all()


@router.post("/procedimentos", response_model=schemas.Procedimento)
def create_procedimento(
    payload: schemas.ProcedimentoCreate,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.CLINICO.value, Role.ADMIN_TENANT.value, Role.FATURAMENTO.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    atendimento = db.get(models.Atendimento, payload.atendimento_id)
    if not atendimento:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado")
    ensure_same_tenant(atendimento.tenant_id, current_tenant_id)
    paciente = db.get(models.Paciente, atendimento.paciente_id)
    profissional = db.get(models.Profissional, atendimento.profissional_id)
    unidade = db.get(models.Unidade, atendimento.unidade_id)
    data_at = atendimento.data.date() if isinstance(atendimento.data, datetime) else atendimento.data

    data = payload.model_dump()
    data["tenant_id"] = current_tenant_id
    proc = models.ProcedimentoSUS(**data)
    tabela_proc = sigtap_rules.get_tabela_para_competencia(db, payload.sigtap_codigo, proc.competencia_aaaamm)
    erros = sigtap_rules.validate_procedimento(db, paciente, proc, unidade, profissional, data_at, tabela_proc=tabela_proc)
    if erros:
        raise HTTPException(status_code=400, detail={"erros": erros})
    obj = _commit_and_refresh(db, proc)
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "CRIAR_PROCEDIMENTO", "ProcedimentoSUS", obj.id)
    return obj


@router.get("/procedimentos", response_model=List[schemas.Procedimento])
def list_procedimentos(
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
    _: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value, Role.AUDITOR_INTERNO.value, Role.CLINICO.value)),
):
    stmt = apply_tenant_filter(select(models.ProcedimentoSUS), models.ProcedimentoSUS, current_tenant_id)
    return db.scalars(stmt).all()


def _competencia_aberta(db: Session, unidade_cnes: str, competencia: str) -> bool:
    stmt = select(models.CompetenciaAberta).where(
        models.CompetenciaAberta.unidade_cnes == unidade_cnes,
        models.CompetenciaAberta.competencia == competencia,
        models.CompetenciaAberta.aberta.is_(True),
    )
    return db.scalars(stmt).first() is not None


def _audit_proc(db: Session, proc: models.ProcedimentoSUS):
    atendimento = db.get(models.Atendimento, proc.atendimento_id)
    paciente = db.get(models.Paciente, atendimento.paciente_id)
    profissional = db.get(models.Profissional, atendimento.profissional_id)
    unidade = db.get(models.Unidade, atendimento.unidade_id)
    tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
    data_at = atendimento.data.date() if isinstance(atendimento.data, datetime) else atendimento.data
    erros = sigtap_rules.validate_procedimento(db, paciente, proc, unidade, profissional, data_at, tabela_proc=tabela)
    competencia_ok = _competencia_aberta(db, unidade.cnes, proc.competencia_aaaamm)
    if not competencia_ok:
        erros.append("competencia_fechada")
    return erros


def audit_competencia_for_tenant(aaaamm: str, tenant_id: int, db: Session):
    stmt = select(models.ProcedimentoSUS).where(
        models.ProcedimentoSUS.competencia_aaaamm == aaaamm,
        models.ProcedimentoSUS.tenant_id == tenant_id,
    )
    procedimentos = db.scalars(stmt).all()
    resultado = []
    for proc in procedimentos:
        erros = _audit_proc(db, proc)
        resultado.append({"procedimento_id": proc.id, "erros": erros})
    return {"competencia": aaaamm, "erros": resultado}


@router.get("/audit/competencia/{aaaamm}")
def audit_competencia(
    aaaamm: str,
    db: Session = Depends(get_db_session),
    current_tenant_id: int = Depends(get_current_tenant_id),
    _: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value, Role.AUDITOR_INTERNO.value)),
):
    return audit_competencia_for_tenant(aaaamm, current_tenant_id, db)


def _garante_dir(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


@router.api_route("/exports/bpa", methods=["GET", "POST"])
def export_bpa_endpoint(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    audit = audit_competencia_for_tenant(competencia, current_tenant_id, db=db)
    erros_globais = [e for item in audit["erros"] for e in item["erros"] if e]
    if erros_globais:
        raise HTTPException(status_code=400, detail={"erros": erros_globais})
    stmt = select(models.ProcedimentoSUS).where(
        models.ProcedimentoSUS.competencia_aaaamm == competencia,
        models.ProcedimentoSUS.tenant_id == current_tenant_id,
    )
    procedimentos = db.scalars(stmt).all()
    linhas = []
    for proc in procedimentos:
        atendimento = db.get(models.Atendimento, proc.atendimento_id)
        paciente = db.get(models.Paciente, atendimento.paciente_id)
        profissional = db.get(models.Profissional, atendimento.profissional_id)
        unidade = db.get(models.Unidade, atendimento.unidade_id)
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        doc = sigtap_rules.decide_documento_bpa(paciente, tabela)
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
            "valor": proc.valores.get("valor", 0) if proc.valores else 0,
        })
    conteudo = export_bpa.gerar_arquivo(
        competencia=competencia,
        orgao="CER",
        sigla="CER",
        cnpj="00000000000000",
        destino="M",
        versao="0.1.0",
        procedimentos=linhas,
    )
    destino_path = Path("exports/bpa") / f"bpa_{competencia}.rem"
    _garante_dir(destino_path)
    destino_path.write_text(conteudo, encoding="utf-8")
    key = f"exports/bpa/bpa_{competencia}.rem"
    uploaded_key = minio_service.upload_bytes(key, conteudo.encode("ascii", errors="ignore"))
    presigned = minio_service.presign_get(uploaded_key) if uploaded_key else None

    unidade_ref = db.scalars(select(models.Unidade).where(models.Unidade.tenant_id == current_tenant_id)).first()
    exp = models.ExportacaoBPA(
        tenant_id=current_tenant_id,
        competencia=competencia,
        unidade_id=unidade_ref.id if unidade_ref else None,
        arquivo_path=presigned or str(destino_path),
        checksum="",
        status="gerado",
        erros_json={},
    )
    db.add(exp)
    db.commit()
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "EXPORTAR_BPA", "ExportacaoBPA", exp.id)

    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return {"url": presigned or str(destino_path), "preview": conteudo[:400]}

    filename = f"BPA_{competencia}.rem"
    return _build_download_response(conteudo, filename)


@router.api_route("/exports/apac", methods=["GET", "POST"])
def export_apac_endpoint(
    request: Request,
    competencia: str = Query(..., min_length=6, max_length=6),
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(Role.FATURAMENTO.value, Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    audit = audit_competencia_for_tenant(competencia, current_tenant_id, db=db)
    erros_globais = [e for item in audit["erros"] for e in item["erros"] if e]
    if erros_globais:
        raise HTTPException(status_code=400, detail={"erros": erros_globais})
    procedimentos = db.scalars(select(models.ProcedimentoSUS).where(
        models.ProcedimentoSUS.competencia_aaaamm == competencia,
        models.ProcedimentoSUS.tenant_id == current_tenant_id,
    )).all()
    procedimentos_apac = []
    for proc in procedimentos:
        tabela = sigtap_rules.get_tabela_para_competencia(db, proc.sigtap_codigo, proc.competencia_aaaamm)
        if tabela and tabela.exige_apac:
            procedimentos_apac.append(proc)
    if not procedimentos_apac:
        raise HTTPException(status_code=400, detail="Nenhum procedimento exige APAC nesta competencia")
    proc = procedimentos_apac[0]
    atendimento = db.get(models.Atendimento, proc.atendimento_id)
    paciente = db.get(models.Paciente, atendimento.paciente_id)
    profissional = db.get(models.Profissional, atendimento.profissional_id)
    unidade = db.get(models.Unidade, atendimento.unidade_id)
    corpo = {
        "competencia": competencia,
        "numero_apac": "0000000000001",
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
            "numero_apac": corpo["numero_apac"],
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
    key = f"exports/apac/apac_{competencia}.rem"
    uploaded_key = minio_service.upload_bytes(key, conteudo.encode("ascii", errors="ignore"))
    presigned = minio_service.presign_get(uploaded_key) if uploaded_key else None
    exp = models.ExportacaoAPAC(
        tenant_id=current_tenant_id,
        competencia=competencia,
        unidade_id=unidade.id,
        arquivo_path=presigned or str(destino_path),
        checksum="",
        status="gerado",
        erros_json={},
    )
    db.add(exp)
    db.commit()
    audit_log_service.log_action(db, current_tenant_id, current_user.id, "EXPORTAR_APAC", "ExportacaoAPAC", exp.id)

    accept = request.headers.get("accept", "")
    if "application/json" in accept:
        return {"url": presigned or str(destino_path), "preview": conteudo[:400]}

    filename = f"APAC_{competencia}.rem"
    return _build_download_response(conteudo, filename)

