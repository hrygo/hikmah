"""Pydantic v2 schemas for Expert Seats."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExpertSeatBase(BaseModel):
    name: str = Field(..., max_length=128, description="Seat identifier name")
    display_name: str = Field(..., max_length=128, description="Human readable display name")
    description: str = Field(default="", max_length=512)
    mattermost_username: str = Field(..., max_length=64, description="Mattermost bot username")
    runtime_type: str = Field(
        default="qwenpaw_shared",
        description="qwenpaw_shared, qwenpaw_personal, agentscope_sidecar",
    )

    runtime_agent_id: str = Field(..., max_length=128, description="Runtime agent reference ID")
    runtime_config: dict[str, object] = Field(default_factory=dict)
    owner_user_id: str | None = Field(default=None, description="Owner ID if personal agent")
    is_personal: bool = Field(default=False)
    status: str = Field(default="active")


class ExpertSeatCreate(ExpertSeatBase):
    mattermost_user_id: str = Field(..., max_length=64, description="Mattermost User ID")


class ExpertSeatUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None
    runtime_config: dict[str, object] | None = None
    status: str | None = None


class ExpertSeatResponse(ExpertSeatBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    mattermost_user_id: str
    created_at: datetime
    updated_at: datetime
