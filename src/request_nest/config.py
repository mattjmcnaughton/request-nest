"""Application configuration via environment variables."""

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Application environment."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All environment variables are prefixed with REQUEST_NEST_.
    For example, REQUEST_NEST_HOST, REQUEST_NEST_PORT, etc.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="REQUEST_NEST_",
        extra="ignore",
    )

    # Environment
    environment: Environment = Environment.DEVELOPMENT

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # Database
    database_url: str

    # Authentication
    admin_token: str = "dev-token-change-me"

    # Request limits
    max_body_size: int = 1048576  # 1MB default


settings = Settings()  # type: ignore[missing-argument]  # pydantic-settings loads from env
