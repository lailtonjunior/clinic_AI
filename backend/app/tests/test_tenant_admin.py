from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.main import app
from app.api.deps import get_db_session
from app import models
from app.auth import get_password_hash


def setup_test_app():
    engine = create_engine("sqlite:///:memory:", future=True, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, future=True)
    Base.metadata.create_all(engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db
    return TestingSessionLocal


def seed_super_admin(db_session):
    db = db_session()
    tenant = models.Tenant(name="Seed", cnpj=None)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    admin = models.Usuario(email="super@test.com", nome="Super", hashed_password=get_password_hash("secret"), ativo=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.add(models.TenantUserRole(user_id=admin.id, tenant_id=tenant.id, role=models.Role.SUPER_ADMIN.value, ativo=True))
    db.commit()
    db.close()
    return tenant


def get_token(client: TestClient, tenant_id: int, email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password, "tenant_id": tenant_id})
    assert res.status_code == 200
    return res.json()["access_token"]


def test_super_admin_can_create_and_list_tenants():
    SessionLocal = setup_test_app()
    tenant = seed_super_admin(SessionLocal)
    with TestClient(app) as client:
        token = get_token(client, tenant.id, "super@test.com", "secret")
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/tenants", headers=headers, json={"name": "Novo Tenant", "cnpj": "123"})
        assert res.status_code == 201
        res = client.get("/api/tenants", headers=headers)
        assert res.status_code == 200
        names = [t["name"] for t in res.json()]
        assert "Novo Tenant" in names


def test_admin_tenant_cannot_manage_tenants():
    SessionLocal = setup_test_app()
    db = SessionLocal()
    tenant = models.Tenant(name="Seed", cnpj=None)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    admin = models.Usuario(email="admin@test.com", nome="Admin", hashed_password=get_password_hash("secret"), ativo=True)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.add(models.TenantUserRole(user_id=admin.id, tenant_id=tenant.id, role=models.Role.ADMIN_TENANT.value, ativo=True))
    db.commit()
    db.close()
    with TestClient(app) as client:
        token = get_token(client, tenant.id, "admin@test.com", "secret")
        headers = {"Authorization": f"Bearer {token}"}
        res = client.post("/api/tenants", headers=headers, json={"name": "X"})
        assert res.status_code == 403
