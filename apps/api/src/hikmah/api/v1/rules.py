"""Sidecar Rule Profiles API endpoints."""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hikmah.core.errors import EntityNotFoundError
from hikmah.models.base import get_db_session
from hikmah.models.rule import SidecarRuleProfile
from hikmah.schemas.rule import (
    SidecarRuleProfileCreate,
    SidecarRuleProfileResponse,
    SidecarRuleProfileUpdate,
)

router = APIRouter(prefix="/rules", tags=["Sidecar Rules"])


@router.get("", response_model=list[SidecarRuleProfileResponse])
async def list_rule_profiles(
    session: AsyncSession = Depends(get_db_session),
) -> Sequence[SidecarRuleProfile]:
    """List all channel Sidecar Rule Profiles."""
    result = await session.execute(select(SidecarRuleProfile))
    return result.scalars().all()


@router.post("", response_model=SidecarRuleProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_profile(
    rule_in: SidecarRuleProfileCreate,
    session: AsyncSession = Depends(get_db_session),
) -> SidecarRuleProfile:
    """Create or register a channel Sidecar Rule Profile."""
    rule = SidecarRuleProfile(
        id=f"rule_{uuid.uuid4().hex[:12]}",
        **rule_in.model_dump(),
    )
    session.add(rule)
    await session.flush()
    return rule


@router.get("/channel/{channel_id}", response_model=SidecarRuleProfileResponse)
async def get_rule_by_channel(
    channel_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> SidecarRuleProfile:
    """Get Sidecar rule profile for a specific Mattermost channel."""
    stmt = select(SidecarRuleProfile).where(SidecarRuleProfile.channel_id == channel_id)
    result = await session.execute(stmt)
    rule = result.scalar_one_or_none()
    if not rule:
        raise EntityNotFoundError("SidecarRuleProfile", channel_id)
    return rule


@router.patch("/{rule_id}", response_model=SidecarRuleProfileResponse)
async def update_rule_profile(
    rule_id: str,
    rule_in: SidecarRuleProfileUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> SidecarRuleProfile:
    """Update rule profile parameters."""
    rule = await session.get(SidecarRuleProfile, rule_id)
    if not rule:
        raise EntityNotFoundError("SidecarRuleProfile", rule_id)

    update_data = rule_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)

    await session.flush()
    return rule
