import os
from typing import Dict, Any

from sqlalchemy import select

from app.core.config import settings
from app.database import SessionLocal
from app import models
from app.auth import get_password_hash


def run_seed() -> Dict[str, Any]:
    """
    Seed idempotente para criar tenant + usuario admin com roles SUPER_ADMIN e ADMIN_TENANT.
    Controlado por variaveis:
    - SEED_TENANT_NAME
    - SEED_ADMIN_EMAIL
    - SEED_ADMIN_PASSWORD
    """
    if not (settings.seed_tenant_name and settings.seed_admin_email and settings.seed_admin_password):
        return {"status": "skipped", "reason": "variaveis de seed nao configuradas"}

    session = SessionLocal()
    try:
        tenant = session.scalars(select(models.Tenant).where(models.Tenant.name == settings.seed_tenant_name)).first()
        if not tenant:
            tenant = models.Tenant(name=settings.seed_tenant_name, cnpj=None)
            session.add(tenant)
            session.commit()
            session.refresh(tenant)

        user = session.scalars(select(models.Usuario).where(models.Usuario.email == settings.seed_admin_email)).first()
        if not user:
            user = models.Usuario(
                email=settings.seed_admin_email,
                nome="Admin Seed",
                hashed_password=get_password_hash(settings.seed_admin_password),
                ativo=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)

        # Roles obrigatorias
        desired_roles = [
            (tenant.id, models.Role.ADMIN_TENANT.value),
            (tenant.id, models.Role.SUPER_ADMIN.value),
        ]
        created_roles = 0
        for tenant_id, role in desired_roles:
            exists = session.scalars(
                select(models.TenantUserRole).where(
                    models.TenantUserRole.user_id == user.id,
                    models.TenantUserRole.tenant_id == tenant_id,
                    models.TenantUserRole.role == role,
                )
            ).first()
            if not exists:
                tur = models.TenantUserRole(user_id=user.id, tenant_id=tenant_id, role=role, ativo=True)
                session.add(tur)
                created_roles += 1
        session.commit()

        return {
            "status": "ok",
            "tenant_id": tenant.id,
            "user_id": user.id,
            "roles_created": created_roles,
            "email": user.email,
        }
    finally:
        session.close()


def main():
    result = run_seed()
    print(f"[seed_initial_admin] {result}")


if __name__ == "__main__":
    main()
