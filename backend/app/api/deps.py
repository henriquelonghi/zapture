from fastapi import Depends, HTTPException, status

from app.core.security import get_current_client
from app.db.session import get_db
from app.models import Client

__all__ = ["get_current_client", "get_db", "require_active_plan"]


def require_active_plan(client: Client = Depends(get_current_client)) -> Client:
    """Conectar uma fonte de dado exige plano ativo (pago) — ver
    app/billing/. Ver relatório continua liberado sem plano (não tem dado
    nenhum conectado mesmo, então não há nada sensível a proteger ali)."""
    if client.plan_status != "active":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Assine o plano pra conectar uma fonte de dados.",
        )
    return client
