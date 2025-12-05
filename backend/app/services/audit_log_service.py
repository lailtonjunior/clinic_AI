from typing import Any, Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app import models


def log_action(
    db: Session,
    tenant_id: int,
    user_id: int,
    acao: str,
    entidade: str,
    entidade_id: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> models.AuditLog:
    audit = models.AuditLog(
        tenant_id=tenant_id,
        user_id=user_id,
        acao=acao,
        entidade=entidade,
        entidade_id=str(entidade_id) if entidade_id is not None else None,
        meta_json=metadata or {},
        criado_em=datetime.utcnow(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
