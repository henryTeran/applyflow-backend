"""
Application configuration using Pydantic BaseSettings.
Loads settings from environment variables and .env file.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = Field(default="ApplyFlow API", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    
    # Database
    database_url: str = Field(
        ...,  # Required
        alias="DATABASE_URL",
        description="PostgreSQL connection string"
    )
    
    # SMTP Configuration
    smtp_host: str = Field(..., alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_user: str = Field(..., alias="SMTP_USER")
    smtp_password: str = Field(..., alias="SMTP_PASSWORD")
    smtp_from: str = Field(..., alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    
    # OpenAI API
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    
    # JWT Authentication
    secret_key: str = Field(
        default="your-secret-key-change-in-production-PLEASE",
        alias="SECRET_KEY",
        description="Secret key for JWT token generation"
    )
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60,
        alias="RATE_LIMIT_PER_MINUTE"
    )
    
    # Redis (for Celery and rate limiting)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        alias="REDIS_URL"
    )
    
    # File Storage
    generated_docs_path: str = Field(
        default="./generated_docs",
        alias="GENERATED_DOCS_PATH"
    )
    upload_path: str = Field(
        default="./uploads",
        alias="UPLOAD_PATH"
    )
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        alias="MAX_UPLOAD_SIZE"
    )
    
    # Validators pour la production
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Ensure SECRET_KEY is changed in production."""
        if not info.data.get("debug", False):
            if len(v) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters in production")
            if "change" in v.lower() or "your-secret" in v.lower():
                raise ValueError("SECRET_KEY must be changed from default value in production")
        return v
    
    @field_validator("smtp_password")
    @classmethod
    def validate_smtp_password(cls, v, info):
        """Ensure SMTP is configured in production."""
        if not info.data.get("debug", False):
            if v in ["your_mot_de_passe", "your-app-password", "votre_mot_de_passe"]:
                raise ValueError("SMTP credentials must be configured in production")
        return v
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v, info):
        """Ensure database uses SSL in production."""
        if not info.data.get("debug", False):
            if "sslmode" not in v.lower():
                import warnings
                warnings.warn("Database URL should include sslmode=require in production")
        return v


# Global settings instance
settings = Settings()
