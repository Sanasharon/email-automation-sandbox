from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables and .env file."""

    # --- Database ---
    database_url: str

    # --- Supabase ---
    supabase_url: str
    supabase_service_role_key: str
    supabase_storage_bucket: str = "email-attachments"

    # --- Runtime ---
    environment: str = "development"

    # --- Scheduler ---
    enable_scheduler: bool = False
    scheduler_enabled: bool = False
    sync_interval_minutes: int = 10
    scheduler_timezone: str = "UTC"
    max_sync_instances: int = 1
    sync_misfire_grace_seconds: int = 300
    sync_lock_ttl_minutes: int = 20

    # --- Security ---
    token_encryption_key: str
    jwt_secret: str
    jwt_expires_in_minutes: int = 1440

    # --- Google OAuth ---
    google_client_secrets_file: str = "secrets/credentials.json"
    google_token_file: str = "secrets/token.json"
    google_oauth_scopes: str = "https://www.googleapis.com/auth/gmail.readonly"

    # --- Sync Limits ---
    max_emails_per_sync: int = 50
    max_attachments_per_sync: int = 10
    max_attachment_size_mb: int = 15

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
