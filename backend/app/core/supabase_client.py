"""Cliente admin do Supabase — usado só pra Storage (guardar o arquivo original
de cada upload, pra auditoria/reprocessamento). Se as credenciais não estiverem
configuradas (ex: ambiente de dev sem Supabase ainda), o upload segue normal e
essa etapa é simplesmente pulada — não é crítica pro motor funcionar."""

from functools import lru_cache

from supabase import Client as SupabaseClient
from supabase import create_client

from app.core.config import get_settings

UPLOADS_BUCKET = "raw-uploads"


@lru_cache
def get_supabase_admin_client() -> SupabaseClient | None:
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        return None
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def store_raw_upload(client_id: str, filename: str, content: bytes) -> str | None:
    """Best-effort: falha de storage nunca deve derrubar o upload (o dado já foi
    ingerido no banco, que é o que importa pro motor)."""
    supabase = get_supabase_admin_client()
    if supabase is None:
        return None
    path = f"{client_id}/{filename}"
    try:
        supabase.storage.from_(UPLOADS_BUCKET).upload(path, content, {"upsert": "true"})
    except Exception:
        return None
    return path
