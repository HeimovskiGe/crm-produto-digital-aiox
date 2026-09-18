"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    app_name: str = "CRM Produto Digital"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/crm"

    # Evolution API (WhatsApp)
    evolution_api_url: str = ""
    evolution_api_key: str = ""
    evolution_instance_name: str = "meu-crm"

    # Kiwify
    kiwify_webhook_secret: str = ""
    kiwify_checkout_url: str = ""

    # WhatsApp Group
    wa_group_jid: str = ""

    # OpenAI (opcional)
    openai_api_key: str = ""

    # Supabase do pam-geh (bancos de empresarios ja scraped - leitura/escrita
    # direto na fonte, sem migrar nada pra este projeto)
    pamgeh_supabase_url: str = ""
    pamgeh_service_role_key: str = ""

    # Google Calendar (horarios livres pra agendar Reuniao de Venda)
    app_base_url: str = "http://localhost:8000"
    google_client_id: str = ""
    google_client_secret: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
