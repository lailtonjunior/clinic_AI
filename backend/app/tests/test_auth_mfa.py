import pytest
import pyotp
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


def _seed_user(SessionLocal, *, enable_mfa: bool = False, secret: str | None = None):
    db = SessionLocal()
    tenant = models.Tenant(name="Tenant Teste")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    user = models.Usuario(
        email="user@test.com",
        nome="User",
        hashed_password=get_password_hash("secret"),
        ativo=True,
        mfa_enabled=enable_mfa,
        mfa_secret=secret,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    role = models.TenantUserRole(user_id=user.id, tenant_id=tenant.id, role=models.Role.SUPER_ADMIN.value, ativo=True)
    db.add(role)
    db.commit()
    db.close()
    return tenant, user


@pytest.fixture
def client():
    SessionLocal, engine = _setup_db()
    tenant, user = _seed_user(SessionLocal)
    with TestClient(app) as c:
        c.tenant = tenant
        c.user = user
        c.SessionLocal = SessionLocal
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_mfa_setup_generates_secret_and_uri(client: TestClient):
    res_login = client.post("/api/auth/login", json={"email": "user@test.com", "password": "secret", "tenant_id": 1})
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post("/api/auth/mfa/setup", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "otpauth_uri" in data
    # Secret is stored, not returned explicitly.
    db = client.SessionLocal()
    stored = db.get(models.Usuario, client.user.id)
    assert stored.mfa_secret is not None
    db.close()


def test_mfa_confirm_with_correct_and_incorrect_code(client: TestClient):
    # Setup MFA to get secret
    res_login = client.post("/api/auth/login", json={"email": "user@test.com", "password": "secret", "tenant_id": 1})
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    res = client.post("/api/auth/mfa/setup", headers=headers)
    assert res.status_code == 200

    db = client.SessionLocal()
    user = db.get(models.Usuario, client.user.id)
    secret = user.mfa_secret
    db.close()
    assert secret

    # Incorrect code
    res_bad = client.post("/api/auth/mfa/confirm", json={"code": "000000"}, headers=headers)
    assert res_bad.status_code == 400

    # Correct code
    code = pyotp.TOTP(secret).now()
    res_ok = client.post("/api/auth/mfa/confirm", json={"code": code}, headers=headers)
    assert res_ok.status_code == 200
    data = res_ok.json()
    assert data["mfa_enabled"] is True


def test_login_requires_mfa_when_enabled(client: TestClient):
    secret = pyotp.random_base32()
    db = client.SessionLocal()
    user = db.get(models.Usuario, client.user.id)
    user.mfa_enabled = True
    user.mfa_secret = secret
    db.add(user)
    db.commit()
    db.close()

    # Missing code
    res_missing = client.post("/api/auth/login", json={"email": "user@test.com", "password": "secret", "tenant_id": 1})
    assert res_missing.status_code == 401

    # Wrong code
    res_wrong = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "secret", "tenant_id": 1, "mfa_code": "000000"},
    )
    assert res_wrong.status_code == 401

    # Correct code
    code = pyotp.TOTP(secret).now()
    res_ok = client.post(
        "/api/auth/login",
        json={"email": "user@test.com", "password": "secret", "tenant_id": 1, "mfa_code": code},
    )
    assert res_ok.status_code == 200
    assert "access_token" in res_ok.json()
