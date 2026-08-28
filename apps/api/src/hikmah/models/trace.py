"""Correlation Record for cross-system trace and audit without copying messages."""

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from hikmah.models.base import Base


class CorrelationRecord(Base):
    """Correlates Mattermost post, AgentScope run, QwenPaw execution, tools, and approvals."""

    __tablename__ = "correlation_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    # Foundation refs
    channel_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    thread_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    post_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)

    # Agent Runtime refs
    expert_seat_id: Mapped[str] = mapped_column(String(64), nullable=False)
    runtime_session_id: Mapped[str] = mapped_column(String(128), nullable=False)

    # Event & Tool Metadata (Zero copy of private payload)
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)

    tool_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
