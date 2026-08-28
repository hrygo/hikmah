"""Correlation Trace records API endpoints for audit and observability."""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hikmah.models.base import get_db_session
from hikmah.models.trace import CorrelationRecord
from hikmah.schemas.trace import (
    CorrelationRecordCreate,
    CorrelationRecordResponse,
)

router = APIRouter(prefix="/traces", tags=["Correlation Traces"])


@router.get("", response_model=list[CorrelationRecordResponse])
async def list_correlation_records(
    trace_id: str | None = None,
    channel_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Sequence[CorrelationRecord]:
    """Query cross-system correlation audit records."""
    stmt = select(CorrelationRecord)
    if trace_id:
        stmt = stmt.where(CorrelationRecord.trace_id == trace_id)
    if channel_id:
        stmt = stmt.where(CorrelationRecord.channel_id == channel_id)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=CorrelationRecordResponse, status_code=status.HTTP_201_CREATED)
async def record_correlation_event(
    trace_in: CorrelationRecordCreate,
    session: AsyncSession = Depends(get_db_session),
) -> CorrelationRecord:
    """Record an audit/trace event without copying private payload content."""
    record = CorrelationRecord(
        id=f"trace_{uuid.uuid4().hex[:12]}",
        **trace_in.model_dump(),
    )
    session.add(record)
    await session.flush()
    return record
