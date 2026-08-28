"""Knowledge Candidate and Promotion database models."""

from enum import StrEnum

from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hikmah.models.base import Base


class KnowledgeStatus(StrEnum):
    """Review and promotion state of knowledge."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVOKED = "revoked"


class KnowledgeScope(StrEnum):
    """Visibility scope of promoted knowledge."""

    CHANNEL = "channel"
    TEAM = "team"


class KnowledgeCandidate(Base):
    """Unapproved or promoted knowledge extracted from channel discussions."""

    __tablename__ = "knowledge_candidates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Provenance
    source_channel_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    source_thread_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source_post_ids: Mapped[list[str]] = mapped_column(JSON, default=list)
    proposer_user_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Review & Promotion
    status: Mapped[str] = mapped_column(String(32), default=KnowledgeStatus.PROPOSED)
    scope: Mapped[str] = mapped_column(String(32), default=KnowledgeScope.TEAM)
    reviewer_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
