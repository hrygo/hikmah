"""Coordinator Sidecar Service implementing quiet observation and smart mention routing."""

import logging
from collections.abc import Sequence
from dataclasses import dataclass

from hikmah.models.rule import RoutingPolicy, SidecarRuleProfile
from hikmah.models.seat import ExpertSeat

logger = logging.getLogger("hikmah.coordinator")


@dataclass
class RoutingDecision:
    """Decision output from Coordinator Sidecar analysis."""

    should_respond: bool
    selected_seat_id: str | None
    reason: str
    confidence: float


class CoordinatorSidecarService:
    """Implements Hikmah moderation rules for AgentScope sidecar."""

    def evaluate_message(
        self,
        message: str,
        explicit_mentioned_seats: list[str],
        rule_profile: SidecarRuleProfile | None,
        available_seats: Sequence[ExpertSeat],
    ) -> RoutingDecision:
        """Evaluate channel event against silence rules and responder selection."""
        _ = message  # Reserved for semantic routing in future iterations

        # 1. Explicit mention rule: If human explicitly mentioned an expert, sidecar is 100% silent
        if explicit_mentioned_seats:
            return RoutingDecision(
                should_respond=False,
                selected_seat_id=None,
                reason=(
                    "Explicit @ mention detected; Sidecar observing silently without interference"
                ),
                confidence=1.0,
            )

        if not rule_profile:
            return RoutingDecision(
                should_respond=False,
                selected_seat_id=None,
                reason="No rule profile configured for channel; default silent",
                confidence=1.0,
            )

        # 2. Check unmentioned policy
        if rule_profile.unmentioned_policy == RoutingPolicy.SILENT:
            return RoutingDecision(
                should_respond=False,
                selected_seat_id=None,
                reason="Channel policy configured to SILENT",
                confidence=1.0,
            )

        # 3. Single responder policy: Pick at most one primary expert
        if rule_profile.unmentioned_policy == RoutingPolicy.SINGLE_RESPONDER:
            if rule_profile.default_responder_seat_id:
                return RoutingDecision(
                    should_respond=True,
                    selected_seat_id=rule_profile.default_responder_seat_id,
                    reason="Routed to default channel expert responder",
                    confidence=rule_profile.confidence_threshold,
                )

            # Heuristic / fallback to first active shared expert
            active_shared = [
                s for s in available_seats if not s.is_personal and s.status == "active"
            ]
            if active_shared:
                return RoutingDecision(
                    should_respond=True,
                    selected_seat_id=active_shared[0].id,
                    reason=f"Auto-selected primary expert seat {active_shared[0].name}",
                    confidence=0.8,
                )

        return RoutingDecision(
            should_respond=False,
            selected_seat_id=None,
            reason="No eligible responder match threshold",
            confidence=0.0,
        )


coordinator_service = CoordinatorSidecarService()
