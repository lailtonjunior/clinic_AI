from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base
from app import models as all_models  # ensure models are registered
from app.main import app
from app.api.deps import get_db_session
from app.database import get_db as base_get_db
from app import models
from app.auth import get_password_hash


def setup_test_app():
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
    Base.metadata.create_all(engine)

    def override_get_db():
        Base.metadata.create_all(engine)
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db
    app.dependency_overrides[base_get_db] = override_get_db
    return engine, TestingSessionLocal


def seed_admin(SessionLocal):
    db = SessionLocal()
    tenant = models.Tenant(name="Tenant Test", cnpj=None)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    tenant_id = tenant.id

    admin = models.Usuario(
        email="admin@test.com",
        nome="Admin",
        hashed_password=get_password_hash("secret"),
        ativo=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    db.add(
        models.TenantUserRole(
            user_id=admin.id,
            tenant_id=tenant_id,
            role=models.Role.ADMIN_TENANT.value,
            ativo=True,
        )
    )
    db.commit()
    db.close()
    return tenant_id


def get_token(
    client: TestClient,
    tenant_id: int,
    email: str = "admin@test.com",
    password: str = "secret",
) -> str:
    res = client.post(
        "/api/auth/login",
        json={"email": email, "password": password, "tenant_id": tenant_id},
    )
    assert res.status_code == 200
    return res.json()["access_token"]


def test_user_crud_and_reset_password():
    engine, SessionLocal = setup_test_app()
    tenant_id = seed_admin(SessionLocal)

    with TestClient(app) as client:
        token = get_token(client, tenant_id)
        headers = {"Authorization": f"Bearer {token}"}

        # create user
        res = client.post(
            "/api/users",
            headers=headers,
            json={
                "nome": "Clinico",
                "email": "clinico@test.com",
                "senha": "abc123",
                "roles": [models.Role.CLINICO.value],
                "must_change_password": True,
            },
        )
        assert res.status_code == 201
        user_id = res.json()["id"]

        # list users
        res = client.get("/api/users", headers=headers)
        assert res.status_code == 200
        emails = [u["email"] for u in res.json()]
        assert "clinico@test.com" in emails

        # reset password
        res = client.post(
            f"/api/users/{user_id}/reset-password",
            headers=headers,
            json={},
        )
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


def test_user_without_permission_cannot_manage_users():
    engine, SessionLocal = setup_test_app()
    tenant_id = seed_admin(SessionLocal)

    db = SessionLocal()
    recep = models.Usuario(
        email="recep@test.com",
        nome="Recep",
        hashed_password=get_password_hash("secret"),
        ativo=True,
    )
    db.add(recep)
    db.commit()
    db.refresh(recep)

    db.add(
        models.TenantUserRole(
            user_id=recep.id,
            tenant_id=tenant_id,
            role=models.Role.RECEPCAO.value,
            ativo=True,
        )
    )
    db.commit()
    db.close()

    with TestClient(app) as client:
        token = get_token(client, tenant_id, email="recep@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        res = client.post(
            "/api/users",
            headers=headers,
            json={
                "nome": "X",
                "email": "x@test.com",
                "senha": "123",
                "roles": [models.Role.CLINICO.value],
            },
        )
        assert res.status_code == 403

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
