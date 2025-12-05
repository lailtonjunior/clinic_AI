from datetime import datetime, timedelta
from typing import List, Optional

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app import models

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _get_roles_for_tenant(db: Session, user_id: int, tenant_id: int) -> List[str]:
    stmt = select(models.TenantUserRole.role).where(
        models.TenantUserRole.user_id == user_id,
        models.TenantUserRole.tenant_id == tenant_id,
        models.TenantUserRole.ativo.is_(True),
    )
    return [r for r, in db.execute(stmt).all()]


def create_access_token(user_id: int, tenant_id: int, roles: List[str], expires_minutes: Optional[int] = None) -> str:
    expire_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    to_encode = {
        "sub": str(user_id),
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": datetime.utcnow() + expire_delta,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")


def authenticate_user(db: Session, email: str, password: str, tenant_id: int) -> tuple[models.Usuario, List[str]]:
    user = db.scalars(select(models.Usuario).where(models.Usuario.email == email)).first()
    if not user or not user.ativo or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais invalidas")
    roles = _get_roles_for_tenant(db, user.id, tenant_id)
    if not roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario sem acesso ao tenant")
    return user, roles
