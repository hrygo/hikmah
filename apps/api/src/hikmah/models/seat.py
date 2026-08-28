"""Expert Seat binding model for Mattermost Bot and QwenPaw/AgentScope runtime."""

from enum import StrEnum

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from hikmah.models.base import Base


class AgentRuntimeType(StrEnum):
    """Runtime provider type for the agent."""

    QWENPAW_SHARED = "qwenpaw_shared"
    QWENPAW_PERSONAL = "qwenpaw_personal"
    AGENTSCOPE_SIDECAR = "agentscope_sidecar"


class SeatStatus(StrEnum):
    """Lifecycle status of the Expert seat."""

    ACTIVE = "active"
    DISABLED = "disabled"
    DEGRADED = "degraded"


class ExpertSeat(Base):
    """Represents an Expert Seat projected onto Mattermost and bound to an Agent runtime."""

    __tablename__ = "expert_seats"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="")

    # Mattermost projection
    mattermost_user_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    mattermost_username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    # Runtime binding
    runtime_type: Mapped[str] = mapped_column(String(32), default=AgentRuntimeType.QWENPAW_SHARED)
    runtime_agent_id: Mapped[str] = mapped_column(String(128), nullable=False)
    runtime_config: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)

    # Ownership & Privacy (owner_user_id is only set for personal agents)
    owner_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_personal: Mapped[bool] = mapped_column(default=False)

    # Seat status
    status: Mapped[str] = mapped_column(String(32), default=SeatStatus.ACTIVE)
