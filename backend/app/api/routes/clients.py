"""Config do próprio workspace (client) — hoje só o telefone de WhatsApp.
`Client.whatsapp_phone` já existia no modelo desde o job de resumo periódico
(app/notifications/summary_job.py filtra por ele), só faltava endpoint pra
editar."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_client, get_db
from app.models import Client
from app.schemas.client import ClientOut, ClientUpdateIn

router = APIRouter(tags=["client"])

_PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{7,14}$")


@router.get("/me", response_model=ClientOut)
def get_me(client: Client = Depends(get_current_client)) -> Client:
    return client


@router.patch("/me", response_model=ClientOut)
def update_me(
    payload: ClientUpdateIn,
    db: Session = Depends(get_db),
    client: Client = Depends(get_current_client),
) -> Client:
    if payload.whatsapp_phone is not None:
        phone = payload.whatsapp_phone.strip()
        if phone and not _PHONE_PATTERN.match(phone):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Telefone inválido — use formato internacional, só dígitos (ex: 5511999998888).",
            )
        client.whatsapp_phone = phone or None

    db.commit()
    db.refresh(client)
    return client
