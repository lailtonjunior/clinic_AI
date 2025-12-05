from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app import models
from app.auth import decode_token

bearer_scheme = HTTPBearer(auto_error=False)


def _get_token_payload(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
    token = credentials.credentials
    return decode_token(token)


def get_current_user(
    db: Session = Depends(get_db_session), payload: dict = Depends(_get_token_payload)
) -> models.Usuario:
    user_id = int(payload.get("sub", 0))
    user = db.get(models.Usuario, user_id)
    if not user or not user.ativo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario invalido")
    return user


def get_current_tenant_id(payload: dict = Depends(_get_token_payload)) -> int:
    tenant_id = payload.get("tenant_id")
    if tenant_id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tenant nao informado no token")
    return int(tenant_id)


def get_current_roles(payload: dict = Depends(_get_token_payload)) -> List[str]:
    return payload.get("roles", []) or []


def require_roles(*roles: str) -> Callable:
    def _checker(user: models.Usuario = Depends(get_current_user), user_roles: List[str] = Depends(get_current_roles)):
        if any(r in user_roles for r in roles):
            return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissao insuficiente")

    return _checker


def apply_tenant_filter(stmt, model, tenant_id: int):
    if hasattr(model, "tenant_id"):
        return stmt.where(model.tenant_id == tenant_id)
    return stmt


def ensure_same_tenant(entity_tenant_id: int, current_tenant_id: int):
    if entity_tenant_id != current_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso a outro tenant negado")
