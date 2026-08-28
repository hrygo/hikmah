"""QwenPaw & AgentScope Runtime Bridge Service."""

import logging
from typing import Any

import httpx

from hikmah.core.config import settings

logger = logging.getLogger("hikmah.runtime")


class AgentRuntimeBridgeService:
    """Dispatches execution requests to QwenPaw Hub and AgentScope workers."""

    def __init__(self, qwenpaw_url: str = settings.qwenpaw_endpoint) -> None:
        self.qwenpaw_url = qwenpaw_url.rstrip("/")

    async def execute_expert_prompt(
        self,
        agent_id: str,
        prompt: str,
        session_id: str,
        context_refs: list[str] | None = None,
    ) -> dict[str, Any]:
        """Dispatch task to QwenPaw Expert Agent runtime."""
        payload = {
            "agent_id": agent_id,
            "prompt": prompt,
            "session_id": session_id,
            "context_refs": context_refs or [],
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(
                    f"{self.qwenpaw_url}/api/v1/agents/{agent_id}/run", json=payload
                )
                if res.status_code == 200:
                    data: dict[str, Any] = res.json()
                    return data
        except Exception as e:
            logger.warning("QwenPaw runtime unavailable or simulated: %s", e)

        # Mock / fallback response for development
        return {
            "session_id": session_id,
            "agent_id": agent_id,
            "output": f"Simulated expert response from {agent_id} for prompt: {prompt[:40]}...",
            "status": "completed",
            "mock": True,
        }


runtime_bridge = AgentRuntimeBridgeService()
