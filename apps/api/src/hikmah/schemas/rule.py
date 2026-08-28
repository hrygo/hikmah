"""Pydantic v2 schemas for Sidecar Rule Profiles."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SidecarRuleProfileBase(BaseModel):
    channel_id: str = Field(..., max_length=64, description="Mattermost Channel ID")
    channel_name: str = Field(default="", max_length=128)
    explicit_mention_silent: bool = Field(
        default=True,
        description="When message has explicit @, sidecar remains silent",
    )
    unmentioned_policy: str = Field(
        default="single_responder",
        description="Policy when unmentioned: silent, single_responder, moderator_only",
    )
    confidence_threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    default_responder_seat_id: str | None = None
    require_approval_for_write: bool = True
    require_approval_for_external: bool = True


class SidecarRuleProfileCreate(SidecarRuleProfileBase):
    pass


class SidecarRuleProfileUpdate(BaseModel):
    explicit_mention_silent: bool | None = None
    unmentioned_policy: str | None = None
    confidence_threshold: float | None = None
    default_responder_seat_id: str | None = None
    require_approval_for_write: bool | None = None
    require_approval_for_external: bool | None = None


class SidecarRuleProfileResponse(SidecarRuleProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
