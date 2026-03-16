"""Tests for DefaultHealingPatternAdvisor (Phase 3)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from agentic_core.L2_execution.healers.healing_tier_types import HealingInput
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_authorize_and_execute("p2", "test_default_healing_pattern_advisor", "execution_auth")
_emit_validates_capability("p2", "test_default_healing_pattern_advisor", "capability_check")
_emit_routes_to_capability("p2", "test_default_healing_pattern_advisor", "capability_route")
_emit_writes_via_uwg("p2", "test_default_healing_pattern_advisor", "uwg_write")
_emit_blocks_direct_write("p2", "test_default_healing_pattern_advisor", "direct_write_block")
_emit_records_tool_invocation("p2", "test_default_healing_pattern_advisor", "tool_invocation")
_emit_captures_execution_output("p2", "test_default_healing_pattern_advisor", "exec_output")
_emit_dispatches_agent("p3", "test_default_healing_pattern_advisor", "agent_dispatch")
_emit_coordinates_agents("p3", "test_default_healing_pattern_advisor", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_default_healing_pattern_advisor", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_default_healing_pattern_advisor", "healing_outcome")
_emit_escalates_failure("p3", "test_default_healing_pattern_advisor", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_default_healing_pattern_advisor", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_default_healing_pattern_advisor", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_default_healing_pattern_advisor", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_default_healing_pattern_advisor", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_default_healing_pattern_advisor", "eval_metric")
_emit_stores_embedding("p4", "test_default_healing_pattern_advisor", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_default_healing_pattern_advisor", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_default_healing_pattern_advisor", "exec_snapshot_link")
from system_learning.engines.default_healing_pattern_advisor import (
    DefaultHealingPatternAdvisor,
    HealingPattern,
)
from system_learning.ports.healing_pattern_advisor import (
    _MAX_PATTERN_BOOST,
)

_emit_records_execution_trace("p0", "evidence", "test_default_healing_pattern_advisor")
_emit_applies_guardrail("p0", "test_default_healing_pattern_advisor", "p0_governance")
_emit_reads_policy_state("p0", "test_default_healing_pattern_advisor", "policy_binding")
_emit_snapshots_state("p0", "test_default_healing_pattern_advisor", "state_snapshot")
emit_replay_key("p0", "test_default_healing_pattern_advisor")
emit_determinism_digest("p0", "test_default_healing_pattern_advisor")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


def test_default_advisor_without_ml_client() -> None:
    """Default advisor falls back to null when no ML client."""
    advisor = DefaultHealingPatternAdvisor(ml_client=None)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    # Should behave like NullHealingPatternAdvisor
    assert advice["pattern_match"] is False
    assert advice["pattern_name"] is None
    assert advice["pattern_boost"] == 0.0
    assert advice["extra_reason_codes"] == ()


def test_default_advisor_with_ml_client_success() -> None:
    """Default advisor uses ML client when available."""
    mock_client = MagicMock()
    mock_patterns = [
        {
            "pattern_id": "pattern_1",
            "pattern_name": "syntax_error_pattern",
            "confidence_boost": 0.08,
            "description": "Common syntax error pattern",
        },
        {
            "pattern_id": "pattern_2",
            "pattern_name": "import_error_pattern",
            "confidence_boost": 0.05,
            "description": "Import error pattern",
        },
    ]
    mock_client.retrieve_healing_patterns.return_value = mock_patterns

    advisor = DefaultHealingPatternAdvisor(ml_client=mock_client)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    # Should pick highest confidence pattern
    assert advice["pattern_match"] is True
    assert advice["pattern_name"] == "syntax_error_pattern"
    assert advice["pattern_boost"] == 0.08
    assert advice["extra_reason_codes"] == ("pattern_boost=0.08",)

    mock_client.retrieve_healing_patterns.assert_called_once_with(error_signature="test_sig")


def test_default_advisor_no_patterns() -> None:
    """Default advisor returns no match when ML client returns no patterns."""
    mock_client = MagicMock()
    mock_client.retrieve_healing_patterns.return_value = []

    advisor = DefaultHealingPatternAdvisor(ml_client=mock_client)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    assert advice["pattern_match"] is False
    assert advice["pattern_name"] is None
    assert advice["pattern_boost"] == 0.0
    assert advice["extra_reason_codes"] == ()


def test_default_advisor_pattern_boost_capped() -> None:
    """Pattern boost is capped at _MAX_PATTERN_BOOST."""
    mock_client = MagicMock()
    mock_patterns = [
        {
            "pattern_id": "pattern_1",
            "pattern_name": "high_boost_pattern",
            "confidence_boost": 0.20,  # Above max
            "description": "High boost pattern",
        },
    ]
    mock_client.retrieve_healing_patterns.return_value = mock_patterns

    advisor = DefaultHealingPatternAdvisor(ml_client=mock_client)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    # Should be capped at max
    assert advice["pattern_boost"] == _MAX_PATTERN_BOOST
    assert advice["extra_reason_codes"] == (f"pattern_boost={_MAX_PATTERN_BOOST:.2f}",)


def test_default_advisor_handles_ml_client_exception() -> None:
    """Default advisor falls back to null when ML client throws."""
    mock_client = MagicMock()
    mock_client.retrieve_healing_patterns.side_effect = Exception("ML client error")

    advisor = DefaultHealingPatternAdvisor(ml_client=mock_client)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    with patch("system_learning.engines.default_healing_pattern_advisor.logger"):
        advice = advisor.advise(healing_input)

    # Should fall back to null behavior
    assert advice["pattern_match"] is False
    assert advice["pattern_name"] is None
    assert advice["pattern_boost"] == 0.0
    assert advice["extra_reason_codes"] == ()


def test_default_advisor_patterns_without_boost() -> None:
    """Default advisor handles patterns without confidence_boost."""
    mock_client = MagicMock()
    mock_patterns = [
        {
            "pattern_id": "pattern_1",
            "pattern_name": "no_boost_pattern",
            # Missing confidence_boost
            "description": "Pattern without boost",
        },
    ]
    mock_client.retrieve_healing_patterns.return_value = mock_patterns

    advisor = DefaultHealingPatternAdvisor(ml_client=mock_client)

    healing_input = HealingInput(
        error_signature="test_sig",
        failure_type="syntax_error",
        blast_radius_estimate=0.1,
        required_tools=[],
        retry_count=0,
        trace_id="test-trace",
        agent_id="test-agent",
    )

    advice = advisor.advise(healing_input)

    # Should handle missing boost gracefully
    assert advice["pattern_match"] is True
    assert advice["pattern_name"] == "no_boost_pattern"
    assert advice["pattern_boost"] == 0.0  # Default to 0.0
    assert advice["extra_reason_codes"] == ()  # No boost, no reason codes


def test_healing_pattern_type() -> None:
    """HealingPattern type has correct structure."""
    pattern: HealingPattern = {
        "pattern_id": "test_pattern",
        "pattern_name": "Test Pattern",
        "confidence_boost": 0.05,
        "description": "Test pattern description",
    }

    assert pattern["pattern_id"] == "test_pattern"
    assert pattern["pattern_name"] == "Test Pattern"
    assert pattern["confidence_boost"] == 0.05
    assert pattern["description"] == "Test pattern description"
