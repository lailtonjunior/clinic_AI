import os
import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database import Base
from app import models
from app.auth import get_password_hash
from app.api.deps import get_db_session
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


def _seed_users(SessionLocal):
    db = SessionLocal()
    tenant = models.Tenant(name="Tenant Teste")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    admin = models.Usuario(
        email="admin@test.com",
        nome="Admin",
        hashed_password=get_password_hash("secret"),
        ativo=True,
    )
    recep = models.Usuario(
        email="recep@test.com",
        nome="Recepcao",
        hashed_password=get_password_hash("secret"),
        ativo=True,
    )
    db.add_all([admin, recep])
    db.commit()
    db.refresh(admin)
    db.refresh(recep)

    roles = [
        models.TenantUserRole(user_id=admin.id, tenant_id=tenant.id, role=models.Role.SUPER_ADMIN.value, ativo=True),
        models.TenantUserRole(user_id=admin.id, tenant_id=tenant.id, role=models.Role.ADMIN_TENANT.value, ativo=True),
        models.TenantUserRole(user_id=recep.id, tenant_id=tenant.id, role=models.Role.RECEPCAO.value, ativo=True),
    ]
    db.add_all(roles)
    db.commit()
    db.close()
    return tenant


@pytest.fixture
def client():
    SessionLocal, engine = _setup_db()
    tenant = _seed_users(SessionLocal)
    with TestClient(app) as c:
        c.tenant = tenant
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_login_invalid_returns_401(client: TestClient):
    res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "wrong", "tenant_id": 1})
    assert res.status_code == 401


def test_login_valid_token_contains_claims(client: TestClient):
    res = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "secret", "tenant_id": 1})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    decoded = jwt.decode(data["access_token"], settings.secret_key, algorithms=[settings.jwt_algorithm])
    assert decoded.get("sub") is not None
    assert decoded.get("tenant_id") == 1
    assert "SUPER_ADMIN" in decoded.get("roles", []) or "ADMIN_TENANT" in decoded.get("roles", [])


def test_protected_route_without_token_is_unauthorized(client: TestClient):
    res = client.get("/api/audit/competencia/202501")
    assert res.status_code == 401


def test_protected_route_with_wrong_role_is_forbidden(client: TestClient):
    login = client.post("/api/auth/login", json={"email": "recep@test.com", "password": "secret", "tenant_id": 1})
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get("/api/audit/competencia/202501", headers=headers)
    assert res.status_code == 403
