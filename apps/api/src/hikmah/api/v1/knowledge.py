"""Knowledge Candidate and Promotion review API endpoints."""

import uuid
from collections.abc import Sequence

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hikmah.core.errors import EntityNotFoundError
from hikmah.models.base import get_db_session
from hikmah.models.knowledge import KnowledgeCandidate, KnowledgeStatus
from hikmah.schemas.knowledge import (
    KnowledgeCandidateCreate,
    KnowledgeCandidateResponse,
    KnowledgeReviewAction,
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge Promotion"])


@router.get("", response_model=list[KnowledgeCandidateResponse])
async def list_knowledge_candidates(
    status_filter: str | None = None,
    channel_id: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> Sequence[KnowledgeCandidate]:
    """List knowledge candidates with optional status/channel filters."""
    stmt = select(KnowledgeCandidate)
    if status_filter:
        stmt = stmt.where(KnowledgeCandidate.status == status_filter)
    if channel_id:
        stmt = stmt.where(KnowledgeCandidate.source_channel_id == channel_id)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=KnowledgeCandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_candidate(
    cand_in: KnowledgeCandidateCreate,
    session: AsyncSession = Depends(get_db_session),
) -> KnowledgeCandidate:
    """Propose a discussion snippet or summary as a knowledge candidate."""
    candidate = KnowledgeCandidate(
        id=f"know_{uuid.uuid4().hex[:12]}",
        **cand_in.model_dump(),
    )
    session.add(candidate)
    await session.flush()
    return candidate


@router.post("/{candidate_id}/review", response_model=KnowledgeCandidateResponse)
async def review_knowledge_candidate(
    candidate_id: str,
    action: KnowledgeReviewAction,
    session: AsyncSession = Depends(get_db_session),
) -> KnowledgeCandidate:
    """Human-in-the-loop review and promotion of a knowledge candidate."""
    candidate = await session.get(KnowledgeCandidate, candidate_id)
    if not candidate:
        raise EntityNotFoundError("KnowledgeCandidate", candidate_id)

    candidate.reviewer_user_id = action.reviewer_user_id
    candidate.review_notes = action.review_notes
    candidate.status = KnowledgeStatus.APPROVED if action.approved else KnowledgeStatus.REJECTED
    if action.target_scope:
        candidate.scope = action.target_scope

    await session.flush()
    return candidate
