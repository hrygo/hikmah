"""Pydantic v2 schemas for Knowledge Promotion."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeCandidateBase(BaseModel):
    title: str = Field(..., max_length=256)
    summary: str
    content: str
    source_channel_id: str
    source_thread_id: str | None = None
    source_post_ids: list[str] = Field(default_factory=list)
    scope: str = Field(default="team", description="channel, team")


class KnowledgeCandidateCreate(KnowledgeCandidateBase):
    proposer_user_id: str


class KnowledgeReviewAction(BaseModel):
    reviewer_user_id: str
    approved: bool
    review_notes: str | None = None
    target_scope: str | None = None


class KnowledgeCandidateResponse(KnowledgeCandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    proposer_user_id: str
    status: str
    reviewer_user_id: str | None = None
    review_notes: str | None = None
    version: int
    created_at: datetime
    updated_at: datetime
