"""Health and capabilities response schemas."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """System health check response."""

    status: str = "ok"
    version: str = "0.1.0"
    foundation: str = "mattermost"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    environment: str = "development"
