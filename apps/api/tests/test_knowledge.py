"""Unit tests for Knowledge Promotion review workflow."""

import pytest
from httpx import ASGITransport, AsyncClient

from hikmah.main import app


@pytest.mark.asyncio
async def test_knowledge_promotion_workflow() -> None:
    """Test proposing knowledge candidate and approving promotion."""
    payload = {
        "title": "生产环境部署 SOP",
        "summary": "生产发布必须先过 staging 验收，由 Admin 双人复核。",
        "content": "详细步骤：1. 确认 PR 合并；2. 执行迁移；3. 观察指标。",
        "source_channel_id": "chan_devops",
        "proposer_user_id": "user_alice",
        "scope": "team",
    }

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Propose
        res = await client.post("/api/v1/knowledge", json=payload)
        assert res.status_code == 201
        cand_id = res.json()["id"]
        assert res.json()["status"] == "proposed"

        # 2. Review (Approve)
        review_payload = {
            "reviewer_user_id": "user_admin",
            "approved": True,
            "review_notes": "SOP 准确，批准晋升为团队知识库资产",
            "target_scope": "team",
        }
        review_res = await client.post(f"/api/v1/knowledge/{cand_id}/review", json=review_payload)
        assert review_res.status_code == 200
        data = review_res.json()
        assert data["status"] == "approved"
        assert data["reviewer_user_id"] == "user_admin"
