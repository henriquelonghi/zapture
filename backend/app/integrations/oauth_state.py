"""O `state` do OAuth carrega qual client e qual plataforma estão se
conectando — a plataforma devolve esse valor intacto no callback, e como o
callback é uma navegação do navegador (sem o Bearer token do Supabase), é
assim que sabemos pra qual client_id gravar a conexão. Assinado com JWT
(igual ao token do Supabase, mas com secret próprio) pra impedir que alguém
force a gravação de uma conexão em outro client."""

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import get_settings

_ALGORITHM = "HS256"
_TTL_MINUTES = 15


def create_state(client_id: uuid.UUID, platform: str) -> str | None:
    settings = get_settings()
    if not settings.internal_signing_secret:
        return None

    payload = {
        "client_id": str(client_id),
        "platform": platform,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=_TTL_MINUTES),
    }
    return jwt.encode(payload, settings.internal_signing_secret, algorithm=_ALGORITHM)


def decode_state(state: str, expected_platform: str) -> uuid.UUID | None:
    settings = get_settings()
    if not settings.internal_signing_secret:
        return None

    try:
        payload = jwt.decode(state, settings.internal_signing_secret, algorithms=[_ALGORITHM])
    except jwt.PyJWTError:
        return None

    if payload.get("platform") != expected_platform:
        return None

    client_id = payload.get("client_id")
    if not client_id:
        return None

    try:
        return uuid.UUID(client_id)
    except ValueError:
        return None
