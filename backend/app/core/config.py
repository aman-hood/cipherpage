from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CipherPage Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Async Postgres Database connection string
    DATABASE_URL: str = "postgresql+asyncpg://cipheruser:cipherpassword@localhost:5432/cipherpagedb"
    
    # Redis configuration for Celery Broker
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT Auth Config
    SECRET_KEY: str = "super_secret_cipherpage_key_123_change_in_production!" 
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
