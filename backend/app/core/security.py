"""Autenticação via Supabase Auth.

O frontend faz login direto com o Supabase (email/senha) e manda o access
token JWT no header Authorization. Aqui só validamos esse token — não existe
fluxo de login próprio no backend.

Projetos Supabase mais novos assinam o token com uma chave assimétrica
(ES256/RS256, "JWT Signing Keys") em vez do secret compartilhado antigo
(HS256, "Legacy JWT Secret") — os dois formatos estão em uso em projetos
reais dependendo de quando foram criados, então validamos os dois: o `alg`
do header do token (não verificado ainda) decide qual caminho seguir.
"""

from functools import lru_cache

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import Client, ClientMember

_ASYMMETRIC_ALGORITHMS = {"ES256", "RS256"}


@lru_cache
def _get_jwks_client(supabase_url: str) -> PyJWKClient:
    return PyJWKClient(f"{supabase_url}/auth/v1/.well-known/jwks.json")


def _decode_supabase_jwt(token: str) -> dict:
    """leeway=10 absorbs small clock drift between this machine and Supabase's
    auth server — without it, `iat`/`nbf` checks intermittently reject tokens
    issued a second or two "in the future" from our clock's perspective."""
    settings = get_settings()

    try:
        alg = jwt.get_unverified_header(token).get("alg")
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.") from exc

    try:
        if alg in _ASYMMETRIC_ALGORITHMS:
            if not settings.supabase_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="SUPABASE_URL não configurado no servidor.",
                )
            signing_key = _get_jwks_client(settings.supabase_url).get_signing_key_from_jwt(token)
            return jwt.decode(
                token, signing_key.key, algorithms=[alg], audience="authenticated", leeway=10
            )

        if not settings.supabase_jwt_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="SUPABASE_JWT_SECRET não configurado no servidor.",
            )
        return jwt.decode(
            token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated", leeway=10
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido ou expirado.") from exc


def get_current_client(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Client:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de autenticação ausente.")

    token = authorization.split(" ", 1)[1]
    payload = _decode_supabase_jwt(token)
    supabase_user_id = payload.get("sub")
    if not supabase_user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem identificador de usuário.")

    member = db.query(ClientMember).filter(ClientMember.supabase_user_id == supabase_user_id).first()
    if member is not None:
        return member.client

    # Primeiro acesso deste usuário autenticado: provisiona o workspace dele.
    workspace_name = payload.get("email") or "Minha Loja"
    new_client = Client(name=workspace_name)
    db.add(new_client)
    db.flush()
    db.add(ClientMember(client_id=new_client.id, supabase_user_id=supabase_user_id, role="owner"))
    db.commit()
    db.refresh(new_client)
    return new_client
