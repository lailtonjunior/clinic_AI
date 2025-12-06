from datetime import datetime, date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.api.deps import get_db_session
from app.auth import get_password_hash
from app.database import Base
from app.main import app


def _setup_db():
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db
    return TestingSessionLocal, engine


def _seed_data(SessionLocal):
    db = SessionLocal()
    tenant = models.Tenant(name="Tenant Teste")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = models.Usuario(
        email="auditor@test.com",
        nome="Auditor",
        hashed_password=get_password_hash("secret"),
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    role = models.TenantUserRole(user_id=user.id, tenant_id=tenant.id, role=models.Role.FATURAMENTO.value, ativo=True)
    db.add(role)
    db.commit()

    unidade = models.Unidade(
        tenant_id=tenant.id,
        nome="Unidade",
        cnes="1234560",
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
        cns="123456789010010",
        cbo="225120",
    )
    paciente = models.Paciente(
        tenant_id=tenant.id,
        nome="Paciente",
        cpf="12345678901",
        cns="898001160660002",
        nome_social=None,
        nome_mae="Mae",
        sexo="M",
        data_nascimento=date(1990, 1, 1),
        ibge_cod="5300108",
        contato={},
        pcd=False,
        cid_deficiencia=None,
    )
    db.add_all([profissional, paciente])
    db.commit()
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

    proc_ok = models.ProcedimentoSUS(
        tenant_id=tenant.id,
        atendimento_id=atendimento.id,
        sigtap_codigo="0301010030",
        cid10="F329",
        quantidade=1,
        profissional_cbo="225120",
        valores={"valor": 10.0},
        competencia_aaaamm="202501",
        validacoes_json={"ok": True, "erros": [], "avisos": []},
    )
    proc_err = models.ProcedimentoSUS(
        tenant_id=tenant.id,
        atendimento_id=atendimento.id,
        sigtap_codigo="0301010030",
        cid10="F329",
        quantidade=1,
        profissional_cbo="225120",
        valores={"valor": 10.0},
        competencia_aaaamm="202501",
        validacoes_json={"ok": False, "erros": ["dv_cns_prof_invalido"], "avisos": []},
    )
    db.add_all([proc_ok, proc_err])
    db.commit()
    db.close()
    return tenant, user


@pytest.fixture
def client():
    SessionLocal, engine = _setup_db()
    tenant, _ = _seed_data(SessionLocal)
    with TestClient(app) as c:
        c.tenant = tenant
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_auditoria_endpoint_summarizes_erros(client: TestClient):
    login = client.post("/api/auth/login", json={"email": "auditor@test.com", "password": "secret", "tenant_id": 1})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/auditoria/competencia/202501", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_procedimentos"] == 2
    assert data["total_com_erros"] == 1
    erros = {item["tipo"]: item["quantidade"] for item in data["erros_agrupados"]}
    assert erros.get("dv_cns_prof_invalido") == 1
    assert data["exemplos_com_erros"]
    assert data["exemplos_com_erros"][0]["mensagens"] == ["dv_cns_prof_invalido"]
