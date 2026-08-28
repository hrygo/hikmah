"""Unit tests for Sidecar Rule Profiles API."""

import pytest
from httpx import ASGITransport, AsyncClient

from hikmah.main import app


@pytest.mark.asyncio
async def test_create_and_get_rule_profile() -> None:
    """Test creating and retrieving a channel sidecar rule profile."""
    payload = {
        "channel_id": "town-square",
        "channel_name": "Town Square",
        "explicit_mention_silent": True,
        "unmentioned_policy": "single_responder",
        "confidence_threshold": 0.8,
        "require_approval_for_write": True,
        "require_approval_for_external": True,
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/rules", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["channel_id"] == "town-square"
        assert data["explicit_mention_silent"] is True

        get_res = await client.get("/api/v1/rules/channel/town-square")
        assert get_res.status_code == 200
        assert get_res.json()["unmentioned_policy"] == "single_responder"
