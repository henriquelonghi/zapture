from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./dev.db"
    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None
    supabase_jwt_secret: str | None = None
    google_service_account_json: str | None = None
    frontend_origin: str = "http://localhost:5173"
    whatsapp_api_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_api_base_url: str = "https://graph.facebook.com/v20.0"

    backend_public_url: str | None = None
    """Base URL pública do backend (ex: https://api.seudominio.com), usada pra
    montar redirect_uri de OAuth e URLs de webhook — sem isso as integrações
    de plataforma não conseguem se registrar."""
    internal_signing_secret: str | None = None
    """Assina o parâmetro `state` do OAuth (carrega client_id + plataforma) —
    não é o mesmo secret do Supabase, é só nosso, interno."""

    shopify_api_key: str | None = None
    shopify_api_secret: str | None = None
    shopify_scopes: str = "read_orders,read_products,read_inventory,read_customers"

    mercadolivre_client_id: str | None = None
    mercadolivre_client_secret: str | None = None

    nuvemshop_client_id: str | None = None
    nuvemshop_client_secret: str | None = None

    stripe_secret_key: str | None = None
    stripe_price_id: str | None = None
    """Price ID do plano único (R$ 47/mês) criado no Dashboard do Stripe."""
    stripe_webhook_secret: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
