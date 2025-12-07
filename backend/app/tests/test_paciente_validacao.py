from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.api.deps import get_db_session
from app.database import Base
from app.dependencies import get_current_user, get_current_roles, get_current_tenant_id
from app.main import app


def _setup_app():
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
    app.dependency_overrides[get_current_user] = lambda: models.Usuario(
        id=1, email="user@test.com", nome="User", hashed_password="x", ativo=True
    )
    app.dependency_overrides[get_current_roles] = lambda: [models.Role.RECEPCAO.value]
    app.dependency_overrides[get_current_tenant_id] = lambda: 1
    return TestingSessionLocal, engine


@pytest.fixture
def client():
    SessionLocal, engine = _setup_app()
    db = SessionLocal()
    db.add(models.Tenant(id=1, name="Tenant Teste"))
    db.commit()
    db.close()
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_create_paciente_invalid_cpf_returns_422(client: TestClient):
    payload = {
        "tenant_id": 1,
        "nome": "Paciente Teste",
        "cpf": "12345678900",
        "cns": None,
        "nome_social": None,
        "nome_mae": None,
        "sexo": "M",
        "data_nascimento": date(1990, 1, 1).isoformat(),
        "ibge_cod": "1234567",
        "contato": {},
        "pcd": False,
        "cid_deficiencia": None,
    }
    res = client.post("/api/pacientes", json=payload)
    assert res.status_code == 422
    assert "CPF invalido" in res.json()["detail"]
