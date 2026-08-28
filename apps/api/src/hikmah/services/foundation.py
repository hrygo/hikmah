"""Mattermost Collaboration Foundation Service and API client."""

import logging
from typing import Any

import httpx

from hikmah.core.config import settings

logger = logging.getLogger("hikmah.foundation")


class MattermostFoundationService:
    """Client for Mattermost Collaboration Foundation REST API v4."""

    def __init__(
        self,
        base_url: str = settings.mattermost_url,
        token: str = settings.mattermost_bot_token,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def get_server_status(self) -> dict[str, Any]:
        """Probe Mattermost server connectivity."""
        if not self.token:
            # Local mock status when no token configured in dev
            return {"status": "ok", "mock": True, "server": "mattermost-simulated"}

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/api/v4/system/ping", headers=self._headers)
                return {
                    "status": "ok" if res.status_code == 200 else "degraded",
                    "code": res.status_code,
                }
        except Exception as e:
            logger.warning("Failed to connect to Mattermost: %s", e)
            return {"status": "unreachable", "error": str(e)}

    async def post_channel_message(
        self,
        channel_id: str,
        message: str,
        root_id: str | None = None,
        props: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Publish a post into a Mattermost channel/thread."""
        payload: dict[str, Any] = {
            "channel_id": channel_id,
            "message": message,
            "props": props or {},
        }
        if root_id:
            payload["root_id"] = root_id

        if not self.token:
            return {
                "id": "mock_post_id",
                "channel_id": channel_id,
                "message": message,
                "mock": True,
            }

        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(
                f"{self.base_url}/api/v4/posts", json=payload, headers=self._headers
            )
            res.raise_for_status()
            data: dict[str, Any] = res.json()
            return data


foundation_service = MattermostFoundationService()
