"""Envio de mensagens via WhatsApp Cloud API (Meta). Se as credenciais não
estiverem configuradas (ex: ambiente de dev sem conta WhatsApp Business ainda),
o envio é pulado e reportado como falha — nunca derruba o job de resumo
periódico, igual ao padrão já usado em supabase_client.py pra Storage."""

import httpx

from app.core.config import get_settings


def send_whatsapp_message(to_phone: str, message: str) -> bool:
    settings = get_settings()
    if not settings.whatsapp_api_token or not settings.whatsapp_phone_number_id:
        return False

    url = f"{settings.whatsapp_api_base_url}/{settings.whatsapp_phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }
    headers = {"Authorization": f"Bearer {settings.whatsapp_api_token}"}

    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        return False
    return True
