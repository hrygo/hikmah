"""Expert Seats management API endpoints."""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hikmah.core.errors import EntityNotFoundError, UnauthorizedAgentAccessError
from hikmah.models.base import get_db_session
from hikmah.models.seat import ExpertSeat
from hikmah.schemas.seat import (
    ExpertSeatCreate,
    ExpertSeatResponse,
    ExpertSeatUpdate,
)

router = APIRouter(prefix="/seats", tags=["Expert Seats"])


@router.get("", response_model=list[ExpertSeatResponse])
async def list_expert_seats(
    is_personal: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Sequence[ExpertSeat]:
    """List configured Expert Seats with optional filter."""
    stmt = select(ExpertSeat)
    if is_personal is not None:
        stmt = stmt.where(ExpertSeat.is_personal == is_personal)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ExpertSeatResponse, status_code=status.HTTP_201_CREATED)
async def create_expert_seat(
    seat_in: ExpertSeatCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ExpertSeat:
    """Register a new Expert Seat mapped to Mattermost Bot."""
    seat = ExpertSeat(
        id=f"seat_{uuid.uuid4().hex[:12]}",
        **seat_in.model_dump(),
    )
    session.add(seat)
    await session.flush()
    return seat


@router.get("/{seat_id}", response_model=ExpertSeatResponse)
async def get_expert_seat(
    seat_id: str,
    user_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> ExpertSeat:
    """Retrieve an Expert Seat by ID with privacy protection."""
    seat = await session.get(ExpertSeat, seat_id)
    if not seat:
        raise EntityNotFoundError("ExpertSeat", seat_id)

    # Personal agent access boundary
    if seat.is_personal and seat.owner_user_id and user_id and seat.owner_user_id != user_id:
        raise UnauthorizedAgentAccessError(seat_id, user_id)

    return seat


@router.patch("/{seat_id}", response_model=ExpertSeatResponse)
async def update_expert_seat(
    seat_id: str,
    seat_in: ExpertSeatUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> ExpertSeat:
    """Update an Expert Seat configuration."""
    seat = await session.get(ExpertSeat, seat_id)
    if not seat:
        raise EntityNotFoundError("ExpertSeat", seat_id)

    update_data = seat_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(seat, field, value)

    await session.flush()
    return seat
