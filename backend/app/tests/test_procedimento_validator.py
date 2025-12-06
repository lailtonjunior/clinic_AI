from datetime import date, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.services.procedimento_validator import ProcedimentoValidatorService


def _setup_db():
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal, engine


def _build_context(
    db,
    *,
    paciente_cns: str = "898001160660002",
    paciente_sexo: str = "F",
    paciente_nascimento: date = date(2010, 1, 1),
    prof_cns: str = "123456789010010",
    unidade_cnes: str = "1234560",
    tabela_kwargs=None,
):
    tabela_kwargs = tabela_kwargs or {}
    tenant = models.Tenant(name="Tenant Teste")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    unidade = models.Unidade(
        tenant_id=tenant.id,
        nome="Unidade",
        cnes=unidade_cnes,
        cnpj="00000000000000",
        uf="DF",
        ibge_cod="5300108",
        destino="M",
        competencia_params={},
    )
    db.add(unidade)
    db.commit()
    db.refresh(unidade)

    profissional = models.Profissional(
        tenant_id=tenant.id,
        unidade_id=unidade.id,
        nome="Prof",
        cpf="12345678901",
        cns=prof_cns,
        cbo="225120",
        conselho="CRM",
        certificado_publico=None,
    )
    paciente = models.Paciente(
        tenant_id=tenant.id,
        nome="Paciente",
        cpf="12345678901",
        cns=paciente_cns,
        nome_social=None,
        nome_mae="Mae",
        sexo=paciente_sexo,
        data_nascimento=paciente_nascimento,
        ibge_cod="5300108",
        contato={},
        pcd=False,
        cid_deficiencia=None,
    )
    db.add_all([profissional, paciente])
    db.commit()
    db.refresh(unidade)
    db.refresh(profissional)
    db.refresh(paciente)

    atendimento = models.Atendimento(
        tenant_id=tenant.id,
        unidade_id=unidade.id,
        profissional_id=profissional.id,
        paciente_id=paciente.id,
        tipo="consulta",
        data=datetime(2025, 1, 10),
        status="concluido",
    )
    db.add(atendimento)
    db.commit()
    db.refresh(atendimento)

    tabela = models.TabelaSIGTAP(
        codigo=tabela_kwargs.get("codigo", "0301010030"),
        descricao="Procedimento Teste",
        valor=0,
        regras={},
        vigencia=tabela_kwargs.get("vigencia", "202501"),
        exige_cid=tabela_kwargs.get("exige_cid", False),
        exige_apac=tabela_kwargs.get("exige_apac", False),
        doc_paciente=tabela_kwargs.get("doc_paciente", "AMBOS_PERMITIDOS"),
        sexo_permitido=tabela_kwargs.get("sexo_permitido", "A"),
        idade_min=tabela_kwargs.get("idade_min"),
        idade_max=tabela_kwargs.get("idade_max"),
        vigencia_inicio=tabela_kwargs.get("vigencia_inicio", "202401"),
        vigencia_fim=tabela_kwargs.get("vigencia_fim"),
    )
    db.add(tabela)
    db.commit()

    proc = models.ProcedimentoSUS(
        tenant_id=tenant.id,
        atendimento_id=atendimento.id,
        sigtap_codigo=tabela.codigo,
        cid10="F329",
        quantidade=1,
        profissional_cbo="225120",
        valores={"valor": 10.0},
        competencia_aaaamm="202501",
        validacoes_json={},
    )
    return proc, tenant


@pytest.fixture
def db_session():
    SessionLocal, engine = _setup_db()
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_validator_detects_cns_invalido(db_session):
    proc, _ = _build_context(db_session, prof_cns="123")
    validator = ProcedimentoValidatorService(db_session)
    resultado = validator.validar_procedimento(proc)
    assert resultado["ok"] is False
    assert "dv_cns_prof_invalido" in resultado["erros"]


def test_validator_detects_idade_fora_range(db_session):
    proc, _ = _build_context(db_session, paciente_nascimento=date(1950, 1, 1), tabela_kwargs={"idade_max": 10})
    validator = ProcedimentoValidatorService(db_session)
    resultado = validator.validar_procedimento(proc)
    assert resultado["ok"] is False
    assert "idade_superior_limite" in resultado["erros"]


def test_validator_detects_sexo_incompativel(db_session):
    proc, _ = _build_context(db_session, paciente_sexo="F", tabela_kwargs={"sexo_permitido": "M"})
    validator = ProcedimentoValidatorService(db_session)
    resultado = validator.validar_procedimento(proc)
    assert resultado["ok"] is False
    assert "sexo_incompativel" in resultado["erros"]


def test_validator_passes_when_sem_erros(db_session):
    proc, _ = _build_context(
        db_session,
        paciente_sexo="M",
        paciente_nascimento=date(2000, 1, 1),
        tabela_kwargs={"sexo_permitido": "M", "idade_min": 10, "idade_max": 80},
    )
    validator = ProcedimentoValidatorService(db_session)
    resultado = validator.validar_procedimento(proc)
    assert resultado["ok"] is True
    assert resultado["erros"] == []
