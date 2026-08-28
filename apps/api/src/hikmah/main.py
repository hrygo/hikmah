"""Hikmah FastAPI Application Entrypoint."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from hikmah.api.v1.router import api_v1_router
from hikmah.core.config import settings
from hikmah.core.errors import HikmahException
from hikmah.models.base import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application startup and shutdown hooks."""
    # Ensure database schema is initialized for dev/testing
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Hikmah Governance & Orchestration API",
    description=(
        "Lightweight Human-Agent Collaboration Governance Layer "
        "for Mattermost, QwenPaw and AgentScope."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HikmahException)
async def hikmah_exception_handler(_request: Request, exc: HikmahException) -> JSONResponse:
    """Handle domain-specific Hikmah exceptions uniformly."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Fallback handler for unhandled errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal error occurred",
                "details": str(exc) if settings.debug else {},
            }
        },
    )


# Include Versioned API Routes
app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


def get_openapi_schema() -> dict[str, object]:
    """Helper to export OpenAPI schema programmatically."""
    return app.openapi()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("hikmah.main:app", host="0.0.0.0", port=8000, reload=True)
