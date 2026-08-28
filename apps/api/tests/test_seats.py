"""Unit tests for Expert Seats and personal agent privacy."""

import pytest
from httpx import ASGITransport, AsyncClient

from hikmah.main import app


@pytest.mark.asyncio
async def test_create_and_get_expert_seat() -> None:
    """Test registering an Expert Seat and retrieving it."""
    payload = {
        "name": "code_expert",
        "display_name": "Senior Code Reviewer",
        "description": "Reviews PRs and analyzes code quality",
        "mattermost_user_id": "mm_bot_code_001",
        "mattermost_username": "code-expert",
        "runtime_type": "qwenpaw_shared",
        "runtime_agent_id": "qwenpaw_code_v1",
        "is_personal": False,
        "status": "active",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create
        res = await client.post("/api/v1/seats", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "code_expert"
        seat_id = data["id"]

        # Get
        get_res = await client.get(f"/api/v1/seats/{seat_id}")
        assert get_res.status_code == 200
        assert get_res.json()["mattermost_username"] == "code-expert"


@pytest.mark.asyncio
async def test_personal_agent_privacy_protection() -> None:
    """Test that personal agents reject access by unauthorized members."""
    payload = {
        "name": "alice_personal_assistant",
        "display_name": "Alice's Private Assistant",
        "description": "Local personal agent for Alice",
        "mattermost_user_id": "mm_personal_alice_001",
        "mattermost_username": "alice-assistant",
        "runtime_type": "qwenpaw_personal",
        "runtime_agent_id": "local_alice_qwen",
        "owner_user_id": "user_alice",
        "is_personal": True,
        "status": "active",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/seats", json=payload)
        assert res.status_code == 201
        seat_id = res.json()["id"]

        # Access by owner -> 200
        ok_res = await client.get(f"/api/v1/seats/{seat_id}?user_id=user_alice")
        assert ok_res.status_code == 200

        # Access by unauthorized member Bob -> 403 Forbidden
        denied_res = await client.get(f"/api/v1/seats/{seat_id}?user_id=user_bob")
        assert denied_res.status_code == 403
        error = denied_res.json()["error"]
        assert error["code"] == "UNAUTHORIZED_AGENT_ACCESS"
