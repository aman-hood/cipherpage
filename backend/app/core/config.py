from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional
from urllib.parse import urlsplit
from sqlalchemy.engine import URL, make_url

class Settings(BaseSettings):
    PROJECT_NAME: str = "CipherPage API"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Security
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000"

    # Firebase Authentication (server-side Admin SDK uses Application Default Credentials)
    FIREBASE_PROJECT_ID: Optional[str] = None
    FIREBASE_CHECK_REVOKED: bool = True
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    
    # Neon PostgreSQL; no default is allowed so deployments cannot silently use a local database.
    DATABASE_URL: str
    # Optional DDL-capable URL for Alembic only; never inject this into app tasks.
    MIGRATION_DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    DB_CONNECT_TIMEOUT: int = 10

    @model_validator(mode="after")
    def validate_remote_cors_origins(self):
        if self.ENVIRONMENT.lower() in {"production", "prod", "staging"}:
            origins = self.cors_origins
            if not origins:
                raise ValueError("ALLOWED_ORIGINS must contain the HTTPS frontend origin in remote environments")
            for origin in origins:
                parsed = urlsplit(origin)
                if (
                    parsed.scheme != "https"
                    or not parsed.hostname
                    or parsed.path
                    or parsed.query
                    or parsed.fragment
                    or parsed.username
                    or parsed.password
                ):
                    raise ValueError("Remote ALLOWED_ORIGINS entries must be exact HTTPS origins")
        return self
    
    # Background Tasks & Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # AI & Integrations
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-flash"

    # Payments (Stripe)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    def sqlalchemy_database_url(self, configured_url: Optional[str] = None) -> URL:
        """Normalize a PostgreSQL URL and require TLS for remote hosts."""
        url = make_url(configured_url or self.DATABASE_URL)
        if url.drivername == "postgresql":
            url = url.set(drivername="postgresql+psycopg2")
        elif url.drivername not in {"postgresql+psycopg2"}:
            raise ValueError("DATABASE_URL must use PostgreSQL with the psycopg2 driver")

        if url.host and url.host.lower() not in {"localhost", "127.0.0.1", "::1"}:
            sslmode = url.query.get("sslmode")
            if sslmode and sslmode.lower() in {"disable", "allow", "prefer"}:
                raise ValueError("DATABASE_URL must use TLS for remote PostgreSQL hosts")
            if sslmode is None:
                url = url.update_query_dict({"sslmode": "require"})
        return url
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True, 
        extra="ignore"
    )

settings = Settings()
