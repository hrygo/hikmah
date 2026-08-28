"""Unit tests for Coordinator Sidecar evaluation rules."""

from hikmah.models.rule import RoutingPolicy, SidecarRuleProfile
from hikmah.models.seat import ExpertSeat
from hikmah.services.coordinator import coordinator_service


def test_explicit_mention_silent_rule() -> None:
    """Test that explicit @ mention enforces 100% Sidecar silence."""
    rule = SidecarRuleProfile(
        id="rule_1",
        channel_id="chan_dev",
        explicit_mention_silent=True,
        unmentioned_policy=RoutingPolicy.SINGLE_RESPONDER,
    )

    decision = coordinator_service.evaluate_message(
        message="@code-expert please review this PR",
        explicit_mentioned_seats=["code-expert"],
        rule_profile=rule,
        available_seats=[],
    )

    assert decision.should_respond is False
    assert decision.selected_seat_id is None
    assert "Explicit @ mention detected" in decision.reason


def test_unmentioned_single_responder_rule() -> None:
    """Test that unmentioned questions trigger single primary responder selection."""
    expert = ExpertSeat(
        id="seat_qa",
        name="qa_expert",
        display_name="QA Expert",
        mattermost_user_id="mm_qa_1",
        mattermost_username="qa-expert",
        is_personal=False,
        status="active",
        runtime_agent_id="qwenpaw_qa",
    )

    rule = SidecarRuleProfile(
        id="rule_qa_channel",
        channel_id="chan_qa",
        explicit_mention_silent=True,
        unmentioned_policy=RoutingPolicy.SINGLE_RESPONDER,
        default_responder_seat_id="seat_qa",
    )

    decision = coordinator_service.evaluate_message(
        message="Is the staging environment build passing?",
        explicit_mentioned_seats=[],
        rule_profile=rule,
        available_seats=[expert],
    )

    assert decision.should_respond is True
    assert decision.selected_seat_id == "seat_qa"
