"""Health endpoint."""

from fastapi import APIRouter

from hikmah.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Get system health and foundation status."""
    return HealthResponse()
