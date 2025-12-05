from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.api.deps import get_db_session
from app.auth import get_password_hash
from app.dependencies import get_current_tenant_id, get_current_user, require_roles


class UserCreateRequest(BaseModel):
    nome: str
    email: str
    senha: str
    roles: List[str]
    must_change_password: bool = True


class UserUpdateRequest(BaseModel):
    nome: Optional[str] = None
    roles: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ResetPasswordRequest(BaseModel):
    nova_senha: Optional[str] = None


router = APIRouter(prefix="/users", tags=["users"])


def _ensure_admin(user: models.Usuario):
    if not user:
        raise HTTPException(status_code=401, detail="Usuario invalido")


@router.get("", response_model=List[dict])
def list_users(
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.SUPER_ADMIN.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    stmt = select(models.Usuario).join(models.TenantUserRole, models.TenantUserRole.user_id == models.Usuario.id).where(
        models.TenantUserRole.tenant_id == current_tenant_id,
        models.TenantUserRole.ativo.is_(True),
    )
    users = db.scalars(stmt).all()
    result = []
    for user in users:
        roles_stmt = select(models.TenantUserRole.role).where(
            models.TenantUserRole.user_id == user.id,
            models.TenantUserRole.tenant_id == current_tenant_id,
            models.TenantUserRole.ativo.is_(True),
        )
        roles = [r for r, in db.execute(roles_stmt).all()]
        result.append(
            {
                "id": user.id,
                "nome": user.nome,
                "email": user.email,
                "roles": roles,
                "ativo": user.ativo,
                "must_change_password": user.must_change_password,
            }
        )
    return result


@router.post("", status_code=201)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    existing = db.scalars(select(models.Usuario).where(models.Usuario.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ja cadastrado")
    user = models.Usuario(
        email=payload.email,
        nome=payload.nome,
        hashed_password=get_password_hash(payload.senha),
        ativo=True,
        must_change_password=payload.must_change_password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    for role in payload.roles:
        tur = models.TenantUserRole(user_id=user.id, tenant_id=current_tenant_id, role=role, ativo=True)
        db.add(tur)
    db.commit()
    return {"id": user.id, "email": user.email}


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    user = db.get(models.Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    if payload.nome is not None:
        user.nome = payload.nome
    if payload.is_active is not None:
        user.ativo = payload.is_active
    db.add(user)
    db.commit()
    if payload.roles is not None:
        db.query(models.TenantUserRole).filter(
            models.TenantUserRole.user_id == user.id,
            models.TenantUserRole.tenant_id == current_tenant_id,
        ).delete()
        for role in payload.roles:
            db.add(models.TenantUserRole(user_id=user.id, tenant_id=current_tenant_id, role=role, ativo=True))
        db.commit()
    return {"status": "ok"}


@router.delete("/{user_id}")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    user = db.get(models.Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    user.ativo = False
    db.add(user)
    db.commit()
    return {"status": "ok"}


@router.post("/{user_id}/reset-password")
def reset_password(
    user_id: int,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(require_roles(models.Role.ADMIN_TENANT.value, models.Role.SUPER_ADMIN.value)),
    current_tenant_id: int = Depends(get_current_tenant_id),
):
    user = db.get(models.Usuario, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario nao encontrado")
    new_password = payload.nova_senha or "Temp123!"
    user.hashed_password = get_password_hash(new_password)
    user.must_change_password = True
    db.add(user)
    db.commit()
    return {"status": "ok", "senha_temporaria": new_password}
