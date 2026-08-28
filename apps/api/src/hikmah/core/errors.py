"""Structured error handling for Hikmah."""

from typing import Any

from fastapi import HTTPException, status


class HikmahException(HTTPException):
    """Base domain exception with structured error representation."""

    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        code: str = "HIKMAH_ERROR",
        message: str = "An error occurred in Hikmah governance layer",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(
            status_code=status_code,
            detail={
                "code": self.code,
                "message": self.message,
                "details": self.details,
            },
        )


class EntityNotFoundError(HikmahException):
    """Resource not found error."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="ENTITY_NOT_FOUND",
            message=f"{entity_type} with ID '{entity_id}' was not found",
            details={"entity_type": entity_type, "entity_id": entity_id},
        )


class UnauthorizedAgentAccessError(HikmahException):
    """Personal agent privacy violation error."""

    def __init__(self, agent_id: str, user_id: str) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="UNAUTHORIZED_AGENT_ACCESS",
            message=(
                "Personal agents are strictly owner-only and cannot be accessed by other members"
            ),
            details={"agent_id": agent_id, "attempted_by_user_id": user_id},
        )
