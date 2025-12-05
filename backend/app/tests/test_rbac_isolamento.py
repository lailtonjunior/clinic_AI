from datetime import datetime, date

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from app.dependencies import apply_tenant_filter
from app.api.routes.core import audit_competencia_for_tenant
from app.services import audit_log_service


def _session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, future=True)()


def _seed_basic(db, tenant_id: int):
    tenant = models.Tenant(id=tenant_id, name=f"Tenant {tenant_id}")
    unidade = models.Unidade(id=tenant_id, tenant_id=tenant_id, nome="Unidade", cnes="1234567", cnpj="12345678000199", uf="DF", ibge_cod="5300108", destino="M", competencia_params={})
    prof = models.Profissional(id=tenant_id, tenant_id=tenant_id, unidade_id=tenant_id, nome="Prof", cpf="12345678901", cns="898001160660001", cbo="225120", conselho="CRM")
    pac = models.Paciente(id=tenant_id, tenant_id=tenant_id, nome="Paciente", cpf="12345678901", cns="898001160660002", nome_social=None, nome_mae="Mae", sexo="M", data_nascimento=date(1990, 1, 1), ibge_cod="5300108", contato={}, pcd=False, cid_deficiencia=None)
    at = models.Atendimento(id=tenant_id, tenant_id=tenant_id, unidade_id=tenant_id, profissional_id=tenant_id, paciente_id=tenant_id, tipo="consulta", data=datetime(2025, 1, 1, 10, 0), status="concluido")
    proc = models.ProcedimentoSUS(id=tenant_id, tenant_id=tenant_id, atendimento_id=tenant_id, sigtap_codigo="0301010030", cid10="F329", quantidade=1, profissional_cbo="225120", valores={"valor": 10.0}, competencia_aaaamm="202501", validacoes_json={})
    tab = models.TabelaSIGTAP(codigo="0301010030", descricao="Consulta", valor=10.0, regras={}, vigencia="202501", exige_cid=False, exige_apac=False, doc_paciente="CNS", sexo_permitido="A", idade_min=None, idade_max=None, vigencia_inicio="202501", vigencia_fim=None)
    db.add_all([tenant, unidade, prof, pac, at, proc, tab])
    db.commit()


def test_apply_tenant_filter_isolation():
    db = _session()
    _seed_basic(db, 1)
    _seed_basic(db, 2)
    stmt = apply_tenant_filter(select(models.Paciente), models.Paciente, 1)
    patients = db.scalars(stmt).all()
    assert all(p.tenant_id == 1 for p in patients)
    stmt_b = apply_tenant_filter(select(models.Paciente), models.Paciente, 2)
    patients_b = db.scalars(stmt_b).all()
    assert all(p.tenant_id == 2 for p in patients_b)


def test_audit_competencia_filters_tenant():
    db = _session()
    _seed_basic(db, 1)
    _seed_basic(db, 2)
    res_a = audit_competencia_for_tenant("202501", 1, db)
    ids_a = [item["procedimento_id"] for item in res_a["erros"]]
    res_b = audit_competencia_for_tenant("202501", 2, db)
    ids_b = [item["procedimento_id"] for item in res_b["erros"]]
    assert ids_a and ids_b and set(ids_a).isdisjoint(ids_b)


def test_audit_log_written():
    db = _session()
    audit_log_service.log_action(db, tenant_id=1, user_id=99, acao="TESTE", entidade="Paciente", entidade_id="1")
    rows = db.scalars(select(models.AuditLog)).all()
    assert len(rows) == 1
    assert rows[0].acao == "TESTE"
