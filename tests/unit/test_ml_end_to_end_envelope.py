"""
Phase 4.1 — Wave 3 Tests: End-to-end-shaped mixin enforcement.

Exercises the real mixin call paths (ml_store_healing_pattern, ml_cache_set)
rather than MLWriteIntentExecutor helpers directly.

Proves:
- Both mixin write methods raise MLWriteEnvelopeViolation outside sandbox.
- Both mixin write methods call through to the underlying client inside sandbox.
- Underlying client write methods are NEVER invoked outside sandbox.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_ml_end_to_end_envelope", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_ml_end_to_end_envelope", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_ml_end_to_end_envelope", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_ml_end_to_end_envelope", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_ml_end_to_end_envelope", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_ml_end_to_end_envelope", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_ml_end_to_end_envelope", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_ml_end_to_end_envelope", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_ml_end_to_end_envelope", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_ml_end_to_end_envelope", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_ml_end_to_end_envelope", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_ml_end_to_end_envelope", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_ml_end_to_end_envelope", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_ml_end_to_end_envelope", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_ml_end_to_end_envelope", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_ml_end_to_end_envelope", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_ml_end_to_end_envelope", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_ml_end_to_end_envelope", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_ml_end_to_end_envelope", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_ml_end_to_end_envelope", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_ml_end_to_end_envelope", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_ml_end_to_end_envelope", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_ml_end_to_end_envelope", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_ml_end_to_end_envelope")
# REMOVED: _emit_applies_guardrail("p0", "test_ml_end_to_end_envelope", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_ml_end_to_end_envelope", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_ml_end_to_end_envelope", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_ml_end_to_end_envelope", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_ml_end_to_end_envelope", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ml_end_to_end_envelope", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_ml_end_to_end_envelope", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_ml_end_to_end_envelope", "write_through")
# REMOVED: _emit_writes_through("p1", "test_ml_end_to_end_envelope", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_ml_end_to_end_envelope", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_ml_end_to_end_envelope", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_ml_end_to_end_envelope", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_ml_end_to_end_envelope", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_ml_end_to_end_envelope", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_ml_end_to_end_envelope", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_ml_end_to_end_envelope", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_ml_end_to_end_envelope", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_ml_end_to_end_envelope", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_ml_end_to_end_envelope", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_ml_end_to_end_envelope", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_ml_end_to_end_envelope", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_ml_end_to_end_envelope", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_ml_end_to_end_envelope", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_ml_end_to_end_envelope")
# REMOVED: _emit_gated_by_confidence("p1", "test_ml_end_to_end_envelope", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_ml_end_to_end_envelope")
# REMOVED: emit_determinism_digest("p0", "test_ml_end_to_end_envelope")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_ml_end_to_end_envelope", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_ml_end_to_end_envelope", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_ml_end_to_end_envelope", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_ml_end_to_end_envelope", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_ml_end_to_end_envelope", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_ml_end_to_end_envelope", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_ml_end_to_end_envelope", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_ml_end_to_end_envelope", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_ml_end_to_end_envelope", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_ml_end_to_end_envelope", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_ml_end_to_end_envelope", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_ml_end_to_end_envelope", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_ml_end_to_end_envelope", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_ml_end_to_end_envelope", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_ml_end_to_end_envelope", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_ml_end_to_end_envelope", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_ml_end_to_end_envelope", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_ml_end_to_end_envelope", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_ml_end_to_end_envelope", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_ml_end_to_end_envelope", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Minimal concrete agent that uses the mixin (no real base class needed)
# ---------------------------------------------------------------------------


class _TestAgent(MetaLearningClientMixin):
    """Minimal concrete agent for testing mixin enforcement."""

    _ml_domain = AGENTIC_CORE_DIR

    def __init__(self) -> None:
        MetaLearningClientMixin.reset_ml_singletons()


def _make_agent_with_mock_client() -> tuple[_TestAgent, MagicMock]:
    """Return (agent, mock_client) with the mixin client pre-wired."""
    agent = _TestAgent()
    mock_client = MagicMock()
    mock_client.store_healing_pattern.return_value = "pattern-mock-001"
    mock_client.cache_set.return_value = True
    MetaLearningClientMixin._ml_client = mock_client
    return agent, mock_client


_VIOLATION = {"type": "import_error", "path": "agentic_core/foo.py", "id": "v-001"}
_HEALING_RESULT = {"status": "fixed", "fix": "added import"}
_CACHE_KEY = "ast:result:foo"
_CACHE_VALUE = {"score": 42}


# ---------------------------------------------------------------------------
# Wave 3 — Negative: blocked outside sandbox
# ---------------------------------------------------------------------------


class TestMixinBlockedOutsideSandbox:
    def test_mixin_store_healing_pattern_blocked_outside_sandbox(self):
        """
        from agentic_core.L0_routing.config.path_constants import (
            AGENTIC_CORE_DIR,
        )
        from agentic_core.L2_execution.types.ml_write_intent_types import (
            MLWriteEnvelopeViolation,
            MLWriteIntentExecutor,
            is_commit_sandbox_active,
        )
        from agentic_core.mixins.meta_learning_client_mixin import MetaLearningClientMixin
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
            _emit_agent_executes_agent,
            _emit_applies_guardrail,  # noqa: E402
            _emit_authorize_and_execute,
            _emit_blocks_direct_write,
            _emit_captures_evaluation_metric,
            _emit_captures_execution_output,
            _emit_captures_pattern,
            _emit_captures_runtime_anomaly,
            _emit_checks_agent_registry,
            _emit_coordinates_agents,
            _emit_dispatches_agent,
            _emit_dispatches_execution_plan,
            _emit_dispatches_healing_run,
            _emit_emits_metric_event,
            _emit_escalates_failure,
            _emit_escalates_to_human,
            _emit_execution_terminates_at_uwg,
            _emit_feeds_meta_learning,
            _emit_gated_by_confidence,
            _emit_hard_fails_untranscripted,
            _emit_improves_agent_policy,
            _emit_invokes_eval,
            _emit_invokes_evaluation,
            _emit_links_execution_to_snapshot,
            _emit_links_incident_trace,  # noqa: E402
            _emit_observes_runtime_state,
            _emit_orchestrates_workflow,
            _emit_proposal_commits_routing,
            _emit_pulls_context,
            _emit_reads_environ,
            _emit_reads_policy_state,  # noqa: E402
            _emit_reads_runtime_state,
            _emit_records_execution_trace,  # noqa: E402
            _emit_records_healing_outcome,
            _emit_records_incident_event,
            _emit_records_learning_event,
            _emit_records_telemetry_event,
            _emit_records_tool_invocation,
            _emit_records_workflow_lineage,
            _emit_routes_through,
            _emit_routes_to_agent,
            _emit_routes_to_capability,
            _emit_signs_execution_trace,  # noqa: E402
            _emit_snapshots_state,  # noqa: E402
            _emit_stores_embedding,
            _emit_stores_learning_state,
            _emit_transcripts_response,
            _emit_triggers_alert,
            _emit_updates_meta_learning_state,
            _emit_updates_monitoring_state,
            _emit_updates_routing_strategy,
            _emit_validated_by_safety_plane,
            _emit_validates_agent_capability,
            _emit_validates_capability,
            _emit_verifies_boundary,
            _emit_verifies_policy,
            _emit_writes_learning_snapshot,
            _emit_writes_observability_log,
            _emit_writes_through,  # noqa: E402
            _emit_writes_via_uwg,
            emit_determinism_digest,  # noqa: E402
            emit_replay_key,  # noqa: E402

        ml_store_healing_pattern() called outside L2.2 sandbox MUST raise
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

    def test_mixin_cache_set_blocked_outside_sandbox(self):
        """
        ml_cache_set() called outside L2.2 sandbox MUST raise
        MLWriteEnvelopeViolation with ML_WRITE_OUTSIDE_SANDBOX.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation, match="ML_WRITE_OUTSIDE_SANDBOX"):
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

    def test_store_healing_pattern_client_never_called_outside_sandbox(self):
    """Test store_healing_pattern_client_never_called_outside_sandbox runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute store_healing_pattern_client_never_called_outside_sandbox
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    """Test cache_set_client_never_called_outside_sandbox runtime behavior."""
    # Arrange
    # TODO: Set up execution parameters
    input_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute cache_set_client_never_called_outside_sandbox
    result = None  # Replace with actual execution

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, (dict, list, str, int, float, bool)), "Result should be a common type"
    # TODO: Add specific execution assertions
        with pytest.raises(MLWriteEnvelopeViolation) as exc_info:
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)
        assert "ml_store_healing_pattern" in str(exc_info.value)

    def test_violation_error_message_contains_method_name_cache_set(self):
        agent, _ = _make_agent_with_mock_client()
        with pytest.raises(MLWriteEnvelopeViolation) as exc_info:
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)
        assert "ml_cache_set" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Wave 3 — Positive: allowed inside sandbox, client write IS invoked
# ---------------------------------------------------------------------------


class TestMixinAllowedInsideSandbox:
    def test_mixin_store_healing_pattern_allowed_inside_sandbox_executes_client_write(self):
        """
        ml_store_healing_pattern() inside L2.2 sandbox must call through to
        client.store_healing_pattern() and return the pattern_id.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            result = agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        mock_client.store_healing_pattern.assert_called_once()
        assert result == "pattern-mock-001"

    def test_mixin_cache_set_allowed_inside_sandbox_executes_client_write(self):
        """
        ml_cache_set() inside L2.2 sandbox must call through to
        client.cache_set() and return True.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            result = agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        mock_client.cache_set.assert_called_once()
        assert result is True

    def test_store_healing_pattern_passes_correct_args_to_client(self):
        """Client receives (possibly sanitized) violation, healing_result, and domain."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        call_args = mock_client.store_healing_pattern.call_args
        passed_violation = call_args[0][0]
        # Guardrails may sanitize the violation dict; assert on stable keys only
        assert passed_violation.get("type") == _VIOLATION["type"]
        assert passed_violation.get("path") == _VIOLATION["path"]
        assert call_args[0][1] == _HEALING_RESULT
        assert call_args[0][2] == AGENTIC_CORE_DIR

    def test_cache_set_passes_correct_key_value_to_client(self):
        """Client receives key, value, domain, and ttl."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE, ttl=3600)

        call_args = mock_client.cache_set.call_args
        assert call_args[0][0] == _CACHE_KEY
        assert call_args[0][1] == _CACHE_VALUE

    def test_sandbox_deactivates_after_mixin_write(self):
        """Sandbox must be inactive after the context manager exits."""
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        assert is_commit_sandbox_active() is False

    def test_cache_set_sandbox_deactivates_after_write(self):
        agent, mock_client = _make_agent_with_mock_client()

        with MLWriteIntentExecutor():
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        assert is_commit_sandbox_active() is False


# ---------------------------------------------------------------------------
# Wave 3 — Bypass detection: direct client write outside mixin is also blocked
# ---------------------------------------------------------------------------


class TestDirectClientBypassBlocked:
    def test_direct_client_store_outside_sandbox_not_guarded_by_client(self):
        """
        The client itself has no sandbox guard — enforcement lives in the mixin.
        This test documents that the mixin is the ONLY enforcement seam.
        Calling client.store_healing_pattern directly bypasses the guard,
        which is why the mixin guard is the required enforcement point.
        """
        _, mock_client = _make_agent_with_mock_client()
        # Direct call to mock does not raise — enforcement is in the mixin only
        mock_client.store_healing_pattern(_VIOLATION, _HEALING_RESULT, AGENTIC_CORE_DIR)
        mock_client.store_healing_pattern.assert_called_once()

    def test_mixin_is_sole_enforcement_seam_for_store(self):
        """
        Any code path that reaches client.store_healing_pattern MUST go through
        the mixin. Verify the mixin raises before the client is ever touched.
        """
        agent, mock_client = _make_agent_with_mock_client()
        assert is_commit_sandbox_active() is False

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_store_healing_pattern(_VIOLATION, _HEALING_RESULT)

        # Client was never reached
        mock_client.store_healing_pattern.assert_not_called()

    def test_mixin_is_sole_enforcement_seam_for_cache_set(self):
        """
        Any code path that reaches client.cache_set MUST go through the mixin.
        """
        agent, mock_client = _make_agent_with_mock_client()

        with pytest.raises(MLWriteEnvelopeViolation):
            agent.ml_cache_set(_CACHE_KEY, _CACHE_VALUE)

        mock_client.cache_set.assert_not_called()
