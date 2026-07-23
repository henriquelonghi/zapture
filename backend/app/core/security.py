"""Autenticação via Supabase Auth.

O frontend faz login direto com o Supabase (email/senha) e manda o access
token JWT no header Authorization. Aqui só validamos esse token — não existe
fluxo de login próprio no backend.
"""

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models import Client, ClientMember


def _decode_supabase_jwt(token: str) -> dict:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET não configurado no servidor.",
        )
    try:
        return jwt.decode(token, settings.supabase_jwt_secret, algorithms=["HS256"], audience="authenticated")
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
