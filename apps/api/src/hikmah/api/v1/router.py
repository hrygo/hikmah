"""API v1 root router aggregation."""

from fastapi import APIRouter

from hikmah.api.v1.health import router as health_router
from hikmah.api.v1.knowledge import router as knowledge_router
from hikmah.api.v1.rules import router as rules_router
from hikmah.api.v1.seats import router as seats_router
from hikmah.api.v1.traces import router as traces_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router)
api_v1_router.include_router(seats_router)
api_v1_router.include_router(rules_router)
api_v1_router.include_router(knowledge_router)
api_v1_router.include_router(traces_router)
