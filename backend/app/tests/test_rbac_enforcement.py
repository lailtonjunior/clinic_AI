from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.api.deps import get_db_session
from app.auth import create_access_token
from app.database import Base
from app.main import app


def _setup_db():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine,
        future=True,
    )
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
    tenant = models.Tenant(name="Tenant 1")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = models.Usuario(
        email="user@test.com",
        nome="User",
        hashed_password="x",
        ativo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    unidade_other = models.Unidade(
        tenant_id=tenant.id + 1,
        nome="Outro",
        cnes="7654321",
        cnpj="12345678000199",
        uf="DF",
        ibge_cod="5300108",
        destino="M",
        competencia_params={},
    )
    db.add(unidade_other)
    db.commit()
    db.refresh(unidade_other)

    profissional_other = models.Profissional(
        tenant_id=unidade_other.tenant_id,
        unidade_id=unidade_other.id,
        nome="Prof X",
        cpf="12345678900",
        cns="898001160660006",
        cbo="2251",
        conselho=None,
        certificado_publico=None,
    )
    db.add(profissional_other)
    db.commit()
    db.refresh(profissional_other)

    paciente_other = models.Paciente(
        tenant_id=unidade_other.tenant_id,
        nome="Pac X",
        cpf=None,
        cns="898001160660006",
        nome_social=None,
        nome_mae="Mae",
        sexo="M",
        data_nascimento=datetime(1990, 1, 1).date(),
        ibge_cod="5300108",
        contato={},
        pcd=False,
        cid_deficiencia=None,
    )
    db.add(paciente_other)
    db.commit()
    db.refresh(paciente_other)

    return tenant, user, unidade_other, profissional_other, paciente_other


@pytest.fixture
def client():
    SessionLocal, engine = _setup_db()
    tenant, user, unidade_other, profissional_other, paciente_other = _seed_data(SessionLocal)
    with TestClient(app) as c:
        c.SessionLocal = SessionLocal
        c.tenant = tenant
        c.user = user
        c.unidade_other = unidade_other
        c.profissional_other = profissional_other
        c.paciente_other = paciente_other
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def _auth_headers(user_id: int, tenant_id: int, roles: list[str]):
    token = create_access_token(user_id=user_id, tenant_id=tenant_id, roles=roles, expires_minutes=60)
    return {"Authorization": f"Bearer {token}"}


def test_route_requires_role_returns_403(client: TestClient):
    headers = _auth_headers(client.user.id, client.tenant.id, roles=[models.Role.CLINICO.value])
    res = client.get("/api/tenants", headers=headers)
    assert res.status_code == 403


def test_tenant_isolation_on_payload(client: TestClient):
    headers = _auth_headers(client.user.id, client.tenant.id, roles=[models.Role.CLINICO.value])
    payload = {
        "tenant_id": client.tenant.id,
        "unidade_id": client.unidade_other.id,
        "profissional_id": client.profissional_other.id,
        "paciente_id": client.paciente_other.id,
        "tipo": "CONSULTA",
        "data": datetime(2025, 1, 1, 12, 0, 0).isoformat(),
        "status": "novo",
    }
    res = client.post("/api/atendimentos", json=payload, headers=headers)
    assert res.status_code == 403
