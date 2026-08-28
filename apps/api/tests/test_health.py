"""Unit test for health endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from hikmah.main import app


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test health endpoint returns ok and mattermost foundation info."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["foundation"] == "mattermost"
        assert data["version"] == "0.1.0"
