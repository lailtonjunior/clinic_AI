from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.auth import get_password_hash
from app.dependencies import require_roles


class TenantCreateRequest(BaseModel):
    name: str
    cnpj: Optional[str] = None
    admin_email: Optional[str] = None
    admin_password: Optional[str] = None


class TenantUpdateRequest(BaseModel):
    name: Optional[str] = None
    cnpj: Optional[str] = None


router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("", response_model=List[dict])
def list_tenants(_: models.Usuario = Depends(require_roles(models.Role.SUPER_ADMIN.value)), db: Session = Depends(get_db_session)):
    tenants = db.scalars(select(models.Tenant)).all()
    return [{"id": t.id, "name": t.name, "cnpj": t.cnpj} for t in tenants]


@router.post("", status_code=201)
def create_tenant(
    payload: TenantCreateRequest,
    db: Session = Depends(get_db_session),
    _: models.Usuario = Depends(require_roles(models.Role.SUPER_ADMIN.value)),
):
    existing = db.scalars(select(models.Tenant).where(models.Tenant.name == payload.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tenant ja existe")
    tenant = models.Tenant(name=payload.name, cnpj=payload.cnpj)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    if payload.admin_email and payload.admin_password:
        user = db.scalars(select(models.Usuario).where(models.Usuario.email == payload.admin_email)).first()
        if not user:
            user = models.Usuario(
                email=payload.admin_email,
                nome="Admin Tenant",
                hashed_password=get_password_hash(payload.admin_password),
                ativo=True,
                must_change_password=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        roles = [
            models.TenantUserRole(user_id=user.id, tenant_id=tenant.id, role=models.Role.ADMIN_TENANT.value, ativo=True),
        ]
        for r in roles:
            db.add(r)
        db.commit()
    return {"id": tenant.id, "name": tenant.name}


@router.put("/{tenant_id}")
def update_tenant(
    tenant_id: int,
    payload: TenantUpdateRequest,
    db: Session = Depends(get_db_session),
    _: models.Usuario = Depends(require_roles(models.Role.SUPER_ADMIN.value)),
):
    tenant = db.get(models.Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant nao encontrado")
    if payload.name is not None:
        tenant.name = payload.name
    if payload.cnpj is not None:
        tenant.cnpj = payload.cnpj
    db.add(tenant)
    db.commit()
    return {"status": "ok"}
