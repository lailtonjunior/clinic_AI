from datetime import datetime, date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
import app.api.routes.exports as exports
from app.database import Base
from app.services import minio_service


@pytest.fixture(autouse=True)
def _patch_minio(monkeypatch):
    monkeypatch.setattr(minio_service, "upload_bytes", lambda *args, **kwargs: None)
    monkeypatch.setattr(minio_service, "presign_get", lambda *args, **kwargs: None)


def _make_session():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, future=True)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal


def _seed_minimal(TestingSessionLocal, exige_apac: bool = False):
    db = TestingSessionLocal()
    tenant = models.Tenant(name="Tenant Teste")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    unidade = models.Unidade(
        tenant_id=tenant.id,
        nome="Unidade",
        cnes="1234560",
        cnpj="12345678000199",
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
        nome="Dr Teste",
        cpf="12345678900",
        cns="898001160660006",
        cbo="2251",
        conselho=None,
        certificado_publico=None,
    )
    db.add(profissional)

    paciente = models.Paciente(
        tenant_id=tenant.id,
        nome="Paciente",
        cpf=None,
        cns="898001160660006",
        nome_social=None,
        nome_mae="Mae",
        sexo="M",
        data_nascimento=date(1990, 1, 1),
        ibge_cod="5300108",
        contato={},
        pcd=False,
        cid_deficiencia=None,
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    db.refresh(profissional)

    atendimento = models.Atendimento(
        tenant_id=tenant.id,
        unidade_id=unidade.id,
        profissional_id=profissional.id,
        paciente_id=paciente.id,
        tipo="CONSULTA",
        data=datetime(2025, 1, 1),
        status="realizado",
    )
    db.add(atendimento)
    db.commit()
    db.refresh(atendimento)

    tabela = models.TabelaSIGTAP(
        codigo="1234567890",
        descricao="PROC TESTE",
        valor=10.0,
        regras={},
        vigencia="202501",
        exige_cid=False,
        exige_apac=exige_apac,
        doc_paciente="CNS",
    )
    db.add(tabela)
    db.commit()

    proc = models.ProcedimentoSUS(
        tenant_id=tenant.id,
        atendimento_id=atendimento.id,
        sigtap_codigo="1234567890",
        cid10="A00",
        quantidade=1,
        profissional_cbo="2251",
        valores={"valor": 10.0},
        competencia_aaaamm="202501",
        validacoes_json={},
    )
    db.add(proc)
    db.commit()
    db.refresh(proc)
    db.close()
    return tenant


def test_generate_bpa_from_real_data(tmp_path, monkeypatch):
    TestingSessionLocal = _make_session()
    tenant = _seed_minimal(TestingSessionLocal, exige_apac=False)
    db = TestingSessionLocal()
    conteudo, path = exports._generate_bpa("202501", tenant.id, db)
    linhas = conteudo.splitlines()
    assert len(linhas) == 3
    assert linhas[1].startswith("1234560")
    assert path.endswith(".rem")
    db.close()


def test_generate_apac_from_real_data(tmp_path, monkeypatch):
    TestingSessionLocal = _make_session()
    tenant = _seed_minimal(TestingSessionLocal, exige_apac=True)
    db = TestingSessionLocal()
    conteudo, path = exports._generate_apac("202501", tenant.id, db)
    linhas = conteudo.splitlines()
    assert len(linhas) == 3
    assert linhas[1][266:281] == "898001160660006"  # CNS paciente
    assert path.endswith(".rem")
    db.close()
