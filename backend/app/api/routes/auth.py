from datetime import timedelta
from typing import Optional

import pyotp
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.auth import authenticate_user, create_access_token, verify_password, get_password_hash
from app.core.config import settings
from app.dependencies import get_current_user
from app import models


class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_id: int
    mfa_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: int
    roles: list[str]
    must_change_password: bool


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    user, roles = authenticate_user(db, payload.email, payload.password, payload.tenant_id)
    if user.mfa_enabled:
        if not user.mfa_secret:
            raise HTTPException(status_code=400, detail="MFA habilitado sem secret configurado")
        totp = pyotp.TOTP(user.mfa_secret)
        if not payload.mfa_code or not totp.verify(payload.mfa_code):
            raise HTTPException(status_code=401, detail="Codigo MFA invalido ou ausente")
    token = create_access_token(
        user_id=user.id,
        tenant_id=payload.tenant_id,
        roles=roles,
        expires_minutes=settings.access_token_expire_minutes,
    )
    return TokenResponse(access_token=token, tenant_id=payload.tenant_id, roles=roles, must_change_password=user.must_change_password)


class ChangePasswordRequest(BaseModel):
    senha_atual: str
    senha_nova: str


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(get_current_user),
):
    if not verify_password(payload.senha_atual, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    current_user.hashed_password = get_password_hash(payload.senha_nova)
    current_user.must_change_password = False
    db.add(current_user)
    db.commit()
    return {"status": "ok"}


class MfaSetupResponse(BaseModel):
    otpauth_uri: str


@router.post("/mfa/setup", response_model=MfaSetupResponse)
def mfa_setup(
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(get_current_user),
):
    secret = pyotp.random_base32()
    current_user.mfa_secret = secret
    current_user.mfa_enabled = False
    db.add(current_user)
    db.commit()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=current_user.email, issuer_name=settings.app_name)
    return MfaSetupResponse(otpauth_uri=uri)


class MfaConfirmRequest(BaseModel):
    code: str


@router.post("/mfa/confirm")
def mfa_confirm(
    payload: MfaConfirmRequest,
    db: Session = Depends(get_db_session),
    current_user: models.Usuario = Depends(get_current_user),
):
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA nao inicializado")
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(payload.code):
        raise HTTPException(status_code=400, detail="Codigo MFA invalido")
    current_user.mfa_enabled = True
    db.add(current_user)
    db.commit()
    return {"status": "ok", "mfa_enabled": True}
