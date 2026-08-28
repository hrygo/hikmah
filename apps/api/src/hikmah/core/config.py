"""Hikmah Application Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable fallback."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="HIKMAH_",
    )

    # Core settings
    app_name: str = "Hikmah"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./hikmah.db",
        description="Async database connection string",
    )

    # Mattermost Foundation Settings
    mattermost_url: str = Field(
        default="http://localhost:8065",
        description="Mattermost Server URL",
    )
    mattermost_bot_token: str = Field(
        default="",
        description="Mattermost Bot Access Token",
    )
    mattermost_team_name: str = Field(
        default="hikmah",
        description="Target Mattermost Team Name",
    )

    # QwenPaw Runtime Bridge
    qwenpaw_endpoint: str = Field(
        default="http://localhost:8080",
        description="QwenPaw Hub / Local Runtime Endpoint",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:5173", "http://localhost:8065"],
        description="Allowed CORS origins",
    )


settings = Settings()
