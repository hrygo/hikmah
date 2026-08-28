"""Pydantic v2 schemas for Correlation Trace Records."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CorrelationRecordCreate(BaseModel):
    trace_id: str
    channel_id: str
    thread_id: str | None = None
    post_id: str
    user_id: str
    expert_seat_id: str
    runtime_session_id: str
    action_type: str
    tool_name: str | None = None
    approval_status: str | None = None
    duration_ms: int | None = None
    metadata_json: dict[str, object] = Field(default_factory=dict)


class CorrelationRecordResponse(CorrelationRecordCreate):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
