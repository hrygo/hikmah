"""Unit tests for Correlation Record auditing API."""

import pytest
from httpx import ASGITransport, AsyncClient

from hikmah.main import app


@pytest.mark.asyncio
async def test_record_and_query_correlation_event() -> None:
    """Test recording an audit event and querying by trace_id."""
    payload = {
        "trace_id": "tr_20260828_001",
        "channel_id": "chan_dev",
        "post_id": "post_mm_123",
        "user_id": "user_dev_01",
        "expert_seat_id": "seat_arch",
        "runtime_session_id": "sess_qwen_888",
        "action_type": "tool_execution",
        "tool_name": "git_diff_analyzer",
        "approval_status": "auto_approved",
        "duration_ms": 124,
        "metadata_json": {"files_count": 3},
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.post("/api/v1/traces", json=payload)
        assert res.status_code == 201
        data = res.json()
        assert data["trace_id"] == "tr_20260828_001"
        assert data["tool_name"] == "git_diff_analyzer"

        # Query
        query_res = await client.get("/api/v1/traces?trace_id=tr_20260828_001")
        assert query_res.status_code == 200
        items = query_res.json()
        assert len(items) == 1
        assert items[0]["action_type"] == "tool_execution"
