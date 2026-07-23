"""Credenciais do Google via service account.

Simplificação deliberada pro MVP: em vez de um fluxo OAuth completo (o cliente
loga com a própria conta Google), o cliente compartilha a planilha com o
e-mail da service account configurada no servidor — bem mais simples de
construir e operar sozinho. Um "Sign in with Google" completo pode entrar
depois, se a fricção desse fluxo se mostrar um problema real."""

import json

from google.oauth2 import service_account

from app.core.config import get_settings

SHEETS_READONLY_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


def get_google_service_account_credentials() -> service_account.Credentials | None:
    settings = get_settings()
    if not settings.google_service_account_json:
        return None
    info = json.loads(settings.google_service_account_json)
    return service_account.Credentials.from_service_account_info(info, scopes=SHEETS_READONLY_SCOPES)
