"""Sidecar Rule Profile for Coordinator moderation and routing policies."""

from enum import StrEnum

from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from hikmah.models.base import Base


class RoutingPolicy(StrEnum):
    """Routing policy when message is not explicitly mentioned with @."""

    SILENT = "silent"  # Observe only
    SINGLE_RESPONDER = "single_responder"  # Pick at most one primary expert
    MODERATOR_ONLY = "moderator_only"  # Coordinator summarizes and suggests


class SidecarRuleProfile(Base):
    """Defines channel-level and team-level AgentScope sidecar behavior."""

    __tablename__ = "sidecar_rule_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    channel_name: Mapped[str] = mapped_column(String(128), default="")

    # Silence and mention policies
    explicit_mention_silent: Mapped[bool] = mapped_column(Boolean, default=True)
    unmentioned_policy: Mapped[str] = mapped_column(
        String(32), default=RoutingPolicy.SINGLE_RESPONDER
    )

    # Confidence thresholds
    confidence_threshold: Mapped[float] = mapped_column(Float, default=0.75)
    default_responder_seat_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # HITL approval requirements
    require_approval_for_write: Mapped[bool] = mapped_column(Boolean, default=True)
    require_approval_for_external: Mapped[bool] = mapped_column(Boolean, default=True)
