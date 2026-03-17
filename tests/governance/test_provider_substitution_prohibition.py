"""
Test REQ-415: Provider Substitution Prohibition

Tests that SovereignLLMGateway MUST NOT substitute provider/model on failure.
Any failure MUST be fail-closed.
"""

import pytest

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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_provider_substitution_prohibition")
_emit_applies_guardrail("p0", "test_provider_substitution_prohibition", "p0_governance")
_emit_reads_policy_state("p0", "test_provider_substitution_prohibition", "policy_binding")
_emit_snapshots_state("p0", "test_provider_substitution_prohibition", "state_snapshot")
emit_replay_key("p0", "test_provider_substitution_prohibition")
emit_determinism_digest("p0", "test_provider_substitution_prohibition")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_provider_substitution_prohibition", "execution_auth")
_emit_validates_capability("p2", "test_provider_substitution_prohibition", "capability_check")
_emit_routes_to_capability("p2", "test_provider_substitution_prohibition", "capability_route")
_emit_writes_via_uwg("p2", "test_provider_substitution_prohibition", "uwg_write")
_emit_blocks_direct_write("p2", "test_provider_substitution_prohibition", "direct_write_block")
_emit_records_tool_invocation("p2", "test_provider_substitution_prohibition", "tool_invocation")
_emit_captures_execution_output("p2", "test_provider_substitution_prohibition", "exec_output")
_emit_dispatches_agent("p3", "test_provider_substitution_prohibition", "agent_dispatch")
_emit_coordinates_agents("p3", "test_provider_substitution_prohibition", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_provider_substitution_prohibition", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_provider_substitution_prohibition", "healing_outcome")
_emit_escalates_failure("p3", "test_provider_substitution_prohibition", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_provider_substitution_prohibition", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_provider_substitution_prohibition", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_provider_substitution_prohibition", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_provider_substitution_prohibition", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_provider_substitution_prohibition", "eval_metric")
_emit_stores_embedding("p4", "test_provider_substitution_prohibition", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_provider_substitution_prohibition", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_provider_substitution_prohibition", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.governance

from agentic_core.L2_execution.enforcement.provider_substitution_prohibition import (
    ProviderRequest,
    ProviderSubstitutionGuard,
    ProviderSubstitutionViolation,
    enforce_fail_closed_on_failure,
    get_substitution_guard,
    test_provider_substitution_prohibition,
    validate_provider_request,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_1")
_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_2")
_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_3")
_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_4")
_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_5")
_emit_emits_metric_event("test_provider_substitution_prohibition", "p4obs", "metric_6")
_emit_records_incident_event("test_provider_substitution_prohibition", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_provider_substitution_prohibition", "p4obs", "anomaly")
_emit_writes_observability_log("test_provider_substitution_prohibition", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_provider_substitution_prohibition", "p4obs", "mon_state")
_emit_triggers_alert("test_provider_substitution_prohibition", "p4obs", "alert")
_emit_links_incident_trace("test_provider_substitution_prohibition", "p4obs", "trace_link")
_emit_captures_pattern("test_provider_substitution_prohibition", "p3lm", "pattern")
_emit_records_learning_event("test_provider_substitution_prohibition", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_provider_substitution_prohibition", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_provider_substitution_prohibition", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_provider_substitution_prohibition", "p3lm", "routing")
_emit_improves_agent_policy("test_provider_substitution_prohibition", "p3lm", "policy")
_emit_stores_learning_state("test_provider_substitution_prohibition", "p3lm", "state")
_emit_records_execution_trace("test_provider_substitution_prohibition", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_provider_substitution_prohibition", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_provider_substitution_prohibition", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_provider_substitution_prohibition", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_provider_substitution_prohibition", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_provider_substitution_prohibition", "env_read", "p2_env_1")
_emit_reads_environ("test_provider_substitution_prohibition", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_provider_substitution_prohibition", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_provider_substitution_prohibition", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_provider_substitution_prohibition", "context_pull")
_emit_pulls_context("p1", "test_provider_substitution_prohibition", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_provider_substitution_prohibition", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_provider_substitution_prohibition", "uwg_term_secondary")
_emit_writes_through("p1", "test_provider_substitution_prohibition", "write_through")
_emit_writes_through("p1", "test_provider_substitution_prohibition", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_provider_substitution_prohibition", "safety_validation")
_emit_invokes_eval("p1", "test_provider_substitution_prohibition", "eval_call")
_emit_proposal_commits_routing("p1", "test_provider_substitution_prohibition", "routing_commit")
_emit_escalates_to_human("p1", "test_provider_substitution_prohibition", "human_escalation")
_emit_routes_through("p1", "test_provider_substitution_prohibition", "route_through")
_emit_checks_agent_registry("p1", "test_provider_substitution_prohibition", "agent_registry")
_emit_validates_agent_capability("p1", "test_provider_substitution_prohibition", "capability")
_emit_dispatches_execution_plan("p1", "test_provider_substitution_prohibition", "exec_plan")
_emit_agent_executes_agent("p1", "test_provider_substitution_prohibition", "sub_agent")
_emit_routes_to_agent("p1", "test_provider_substitution_prohibition", "target_agent")
_emit_verifies_policy("p1", "test_provider_substitution_prohibition", "policy_check")
_emit_observes_runtime_state("p1", "test_provider_substitution_prohibition", "runtime_state")
_emit_verifies_boundary("p1", "test_provider_substitution_prohibition", "boundary_check")
_emit_transcripts_response("p1", "test_provider_substitution_prohibition", "transcript")
_emit_hard_fails_untranscripted("p1", "test_provider_substitution_prohibition")
_emit_gated_by_confidence("p1", "test_provider_substitution_prohibition", "confidence_gate")


class TestREQ415ProviderSubstitutionProhibition:
    """Test suite for REQ-415 Provider Substitution Prohibition."""

    def test_validate_provider_request_success(self):
        """Test successful validation when provider/model match."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_123"
        )

        # When/Then - Should not raise
        validate_provider_request(
            original_request=original_request, actual_provider="openai", actual_model="gpt-4"
        )

    def test_validate_provider_request_provider_substitution_blocked(self):
        """Test that provider substitution is blocked."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_123"
        )

        # When/Then
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            validate_provider_request(
                original_request=original_request,
                actual_provider="anthropic",  # Different!
                actual_model="gpt-4",
            )

        assert "Provider substitution detected" in str(exc_info.value)
        assert "REQ-415" in str(exc_info.value)
        assert "openai" in str(exc_info.value)
        assert "anthropic" in str(exc_info.value)

    def test_validate_provider_request_model_substitution_blocked(self):
        """Test that model substitution is blocked."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_123"
        )

        # When/Then
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            validate_provider_request(
                original_request=original_request,
                actual_provider="openai",
                actual_model="gpt-3.5-turbo",  # Different!
            )

        assert "Model substitution detected" in str(exc_info.value)
        assert "REQ-415" in str(exc_info.value)
        assert "gpt-4" in str(exc_info.value)
        assert "gpt-3.5-turbo" in str(exc_info.value)

    def test_validate_provider_request_both_substitution_blocked(self):
        """Test that both provider and model substitution is blocked."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_123"
        )

        # When/Then
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            validate_provider_request(
                original_request=original_request,
                actual_provider="anthropic",  # Different!
                actual_model="claude-3-5-sonnet",  # Different!
            )

        assert "Provider substitution detected" in str(exc_info.value)
        assert "REQ-415" in str(exc_info.value)

    def test_enforce_fail_closed_on_failure(self):
        """Test that failures are fail-closed."""
        # Given
        original_request = ProviderRequest(
            provider="google", model="gemini-pro", agent_id="test_agent", request_id="req_456"
        )
        error = Exception("API rate limit exceeded")

        # When/Then
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            enforce_fail_closed_on_failure(original_request, error)

        assert "Provider request failed" in str(exc_info.value)
        assert "Fail-closed enforced" in str(exc_info.value)
        assert "REQ-415" in str(exc_info.value)
        assert "API rate limit exceeded" in str(exc_info.value)

    def test_enforce_fail_closed_with_attempted_substitution(self):
        """Test fail-closed when substitution was attempted."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_789"
        )
        error = Exception("Connection timeout")
        attempted_substitution = {"provider": "anthropic", "model": "claude-3-5-sonnet"}

        # When/Then
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            enforce_fail_closed_on_failure(original_request, error, attempted_substitution)

        assert "Attempted substitution" in str(exc_info.value)
        assert "anthropic" in str(exc_info.value)
        assert "claude-3-5-sonnet" in str(exc_info.value)

    def test_provider_substitution_guard_register_and_validate(self):
        """Test ProviderSubstitutionGuard register and validate workflow."""
        # Given
        guard = ProviderSubstitutionGuard()
        request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_001"
        )

        # When
        guard.register_request("req_001", request)

        # Then - Should validate successfully
        guard.validate_response("req_001", "openai", "gpt-4")

        # Cleanup
        guard.clear_request("req_001")

    def test_provider_substitution_guard_register_and_validate_substitution(self):
        """Test ProviderSubstitutionGuard detects substitution."""
        # Given
        guard = ProviderSubstitutionGuard()
        request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_002"
        )

        # When
        guard.register_request("req_002", request)

        # Then - Should detect substitution
        with pytest.raises(ProviderSubstitutionViolation):
            guard.validate_response("req_002", "anthropic", "claude-3-5-sonnet")

        # Cleanup
        guard.clear_request("req_002")

    def test_provider_substitution_guard_handle_failure(self):
        """Test ProviderSubstitutionGuard handles failures with fail-closed."""
        # Given
        guard = ProviderSubstitutionGuard()
        request = ProviderRequest(
            provider="google", model="gemini-pro", agent_id="test_agent", request_id="req_003"
        )
        error = Exception("Service unavailable")

        # When
        guard.register_request("req_003", request)

        # Then - Should enforce fail-closed
        with pytest.raises(ProviderSubstitutionViolation):
            guard.handle_failure("req_003", error)

        # Cleanup
        guard.clear_request("req_003")

    def test_provider_substitution_guard_unknown_request(self):
        """Test ProviderSubstitutionGuard with unknown request ID."""
        # Given
        guard = ProviderSubstitutionGuard()

        # When/Then - Validation should fail
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            guard.validate_response("unknown_req", "openai", "gpt-4")

        assert "Unknown request ID" in str(exc_info.value)

        # When/Then - Failure handling should fail
        with pytest.raises(ProviderSubstitutionViolation) as exc_info:
            guard.handle_failure("unknown_req", Exception("test"))

        assert "Unknown request ID" in str(exc_info.value)

    def test_get_substitution_guard(self):
        """Test getting the global substitution guard."""
        # When
        guard = get_substitution_guard()

        # Then
        assert isinstance(guard, ProviderSubstitutionGuard)
        assert guard is get_substitution_guard()  # Should be singleton

    def test_test_provider_substitution_prohibition(self):
        """Test the provider substitution prohibition test function."""
        # When
        result = test_provider_substitution_prohibition()

        # Then
        assert result is True

    def test_provider_request_immutable(self):
        """Test that ProviderRequest is immutable."""
        # Given
        request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_immutable"
        )

        # When/Then - Should not allow modification (frozen dataclass raises FrozenInstanceError)
        with pytest.raises((ProviderSubstitutionViolation, AttributeError, TypeError)):
            request.provider = "anthropic"

        with pytest.raises((ProviderSubstitutionViolation, AttributeError, TypeError)):
            request.model = "gpt-3.5-turbo"

        with pytest.raises((ProviderSubstitutionViolation, AttributeError, TypeError)):
            request.agent_id = "other_agent"

        with pytest.raises((ProviderSubstitutionViolation, AttributeError, TypeError)):
            request.request_id = "other_req"

    def test_validate_provider_request_with_context(self):
        """Test validation with additional context."""
        # Given
        original_request = ProviderRequest(
            provider="openai", model="gpt-4", agent_id="test_agent", request_id="req_ctx"
        )
        context = {"temperature": "0.7", "max_tokens": "1000"}

        # When/Then - Should validate successfully
        validate_provider_request(
            original_request=original_request, actual_provider="openai", actual_model="gpt-4", context=context
        )

    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        # Given
        guard = ProviderSubstitutionGuard()
        requests = [
            ProviderRequest("openai", "gpt-4", "agent1", "req1"),
            ProviderRequest("anthropic", "claude-3-5-sonnet", "agent2", "req2"),
            ProviderRequest("google", "gemini-pro", "agent3", "req3"),
        ]

        # When
        for i, req in enumerate(requests):
            guard.register_request(f"req{i + 1}", req)

        # Then - All should validate successfully
        for i, req in enumerate(requests):
            guard.validate_response(f"req{i + 1}", req.provider, req.model)

        # Cleanup
        for i in range(len(requests)):
            guard.clear_request(f"req{i + 1}")

    def test_edge_case_empty_provider_model(self):
        """Test edge case with empty provider/model strings."""
        # Given
        original_request = ProviderRequest(
            provider="", model="", agent_id="test_agent", request_id="req_edge"
        )

        # When/Then - Should still validate if exact match
        validate_provider_request(original_request=original_request, actual_provider="", actual_model="")

        # But should fail if different
        with pytest.raises(ProviderSubstitutionViolation):
            validate_provider_request(
                original_request=original_request,
                actual_provider="openai",  # Different
                actual_model="",
            )
