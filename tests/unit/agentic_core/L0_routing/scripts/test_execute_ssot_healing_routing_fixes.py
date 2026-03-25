"""
Tests for healing routing bug fixes in execute_ssot.py.

Covers:
1. RuntimeError/OSError/TimeoutError now caught in Qwen except clause
2. SSOT model ID constants used (no os.getenv leaks)
3. Gemini enable_llm boundary condition fixed (conf == 0.50 uses <=)
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_execute_ssot_healing_routing_fixes")
# REMOVED: _emit_applies_guardrail("p0", "test_execute_ssot_healing_routing_fixes", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_execute_ssot_healing_routing_fixes", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_execute_ssot_healing_routing_fixes", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_healing_routing_fixes", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_execute_ssot_healing_routing_fixes", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_execute_ssot_healing_routing_fixes", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_execute_ssot_healing_routing_fixes", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_execute_ssot_healing_routing_fixes", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_execute_ssot_healing_routing_fixes", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_execute_ssot_healing_routing_fixes", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_execute_ssot_healing_routing_fixes", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_execute_ssot_healing_routing_fixes", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_execute_ssot_healing_routing_fixes", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_execute_ssot_healing_routing_fixes", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_execute_ssot_healing_routing_fixes", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_execute_ssot_healing_routing_fixes", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_execute_ssot_healing_routing_fixes", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_healing_routing_fixes", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_healing_routing_fixes", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_healing_routing_fixes", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_healing_routing_fixes", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_healing_routing_fixes", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_execute_ssot_healing_routing_fixes", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_execute_ssot_healing_routing_fixes", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_healing_routing_fixes", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_healing_routing_fixes", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_healing_routing_fixes", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_healing_routing_fixes", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_healing_routing_fixes", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_healing_routing_fixes", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_healing_routing_fixes", "write_through")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_healing_routing_fixes", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_execute_ssot_healing_routing_fixes", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_execute_ssot_healing_routing_fixes", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_execute_ssot_healing_routing_fixes", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_execute_ssot_healing_routing_fixes", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_execute_ssot_healing_routing_fixes", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_execute_ssot_healing_routing_fixes", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_execute_ssot_healing_routing_fixes", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_execute_ssot_healing_routing_fixes", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_execute_ssot_healing_routing_fixes", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_execute_ssot_healing_routing_fixes", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_execute_ssot_healing_routing_fixes", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_execute_ssot_healing_routing_fixes", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_execute_ssot_healing_routing_fixes", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_execute_ssot_healing_routing_fixes", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_execute_ssot_healing_routing_fixes")
# REMOVED: _emit_gated_by_confidence("p1", "test_execute_ssot_healing_routing_fixes", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_execute_ssot_healing_routing_fixes")
# REMOVED: emit_determinism_digest("p0", "test_execute_ssot_healing_routing_fixes")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_execute_ssot_healing_routing_fixes", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_execute_ssot_healing_routing_fixes", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_execute_ssot_healing_routing_fixes", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_execute_ssot_healing_routing_fixes", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_execute_ssot_healing_routing_fixes", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_execute_ssot_healing_routing_fixes", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_execute_ssot_healing_routing_fixes", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_execute_ssot_healing_routing_fixes", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_execute_ssot_healing_routing_fixes", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_execute_ssot_healing_routing_fixes", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_execute_ssot_healing_routing_fixes", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_execute_ssot_healing_routing_fixes", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_execute_ssot_healing_routing_fixes", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_execute_ssot_healing_routing_fixes", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_execute_ssot_healing_routing_fixes", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_execute_ssot_healing_routing_fixes", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_execute_ssot_healing_routing_fixes", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_execute_ssot_healing_routing_fixes", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_execute_ssot_healing_routing_fixes", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_execute_ssot_healing_routing_fixes", "exec_snapshot_link")


class TestQwenExceptionHandling:
    """Test that Qwen failures are properly caught and default to declined (not approved)."""

    def test_qwen_runtime_error_caught_and_defaults_to_declined(self):
        """When Qwen subprocess raises RuntimeError, should catch it and default qwen_approved=False."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        # Mock the Qwen arbiter to raise RuntimeError (subprocess failure)
        def mock_arbiter(*args, **kwargs):
            raise RuntimeError("vLLM subprocess failed: exit code 1")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            # Create a mock confidence score that routes to QWEN tier (0.50 < conf <= 0.80)
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            mock_routing = MagicMock()
            mock_routing.tier = MagicMock()
            mock_routing.tier.value = "QWEN"
            mock_routing.score = 50
            mock_routing.gate_applied = "test_gate"

            # Call should_proceed_with_healing which internally routes to Qwen
            # Since Qwen raises RuntimeError, it should be caught and default to declined
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # After the fix: RuntimeError is caught, qwen_approved defaults to False
            # The Qwen tier then declines and returns False
            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason

    def test_qwen_timeout_error_caught(self):
        """When Qwen subprocess times out, should catch TimeoutError and default to declined."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        def mock_arbiter(*args, **kwargs):
            raise TimeoutError("Qwen subprocess timed out")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason

    def test_qwen_os_error_caught(self):
        """When Qwen subprocess raises OSError (WSL not available), should catch and decline."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=True, auto_approve=False)

        def mock_arbiter(*args, **kwargs):
            raise OSError("WSL not found")

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            mock_confidence = MagicMock()
            mock_confidence.value = 0.65
            mock_confidence.reasoning = "test_violation"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            assert approved is False
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason


class TestSSOTModelIDConstants:
    """Test that model IDs come from SSOT constants, not os.getenv()."""

    def test_qwen_model_id_from_ssot_constant(self):
        """Qwen model ID should come from healing_tier_config.QWEN_14B_MODEL_ID, not os.getenv."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        # Clear any env vars that might interfere
        old_env = os.environ.get("QWEN_14B_MODEL")
        if old_env:
            del os.environ["QWEN_14B_MODEL"]

        try:
            engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

            mock_confidence = MagicMock()
            mock_confidence.value = 0.65  # Routes to QWEN tier
            mock_confidence.reasoning = "test"

            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Check that decision_data uses the SSOT constant, not env var
            # The model ID should be from healing_tier_config.QWEN_14B_MODEL_ID
            assert len(engine.decisions_made) > 0
            decision = engine.decisions_made[-1]
            # Should be the SSOT constant value, not the env var fallback
            assert decision["model"] == "Qwen/Qwen2.5-14B-Instruct-GPTQ-Int4"

        finally:
            if old_env:
                os.environ["QWEN_14B_MODEL"] = old_env

    def test_gemini_model_id_from_ssot_constant(self):
        """Gemini model ID should be hardcoded 'gemini-2.5-pro', not os.getenv."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        old_env = os.environ.get("GEMINI_MODEL")
        if old_env:
            del os.environ["GEMINI_MODEL"]

        try:
            engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

            mock_confidence = MagicMock()
            mock_confidence.value = 0.40  # Routes to GEMINI tier (conf <= 0.50)
            mock_confidence.reasoning = "test"

            # enable_llm=False will block Gemini, but we can check the decision_data model field
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Check decision_data
            assert len(engine.decisions_made) > 0
            decision = engine.decisions_made[-1]
            # Should be the hardcoded SSOT value
            assert decision["model"] == "gemini-2.5-pro"

        finally:
            if old_env:
                os.environ["GEMINI_MODEL"] = old_env


class TestGeminiEnableLLMBoundary:
    """Test that Gemini enable_llm guard uses <= instead of < at conf == 0.50."""

    def test_gemini_boundary_conf_exactly_050_blocked_when_llm_disabled(self):
        """When conf == 0.50 exactly and enable_llm=False, should block (not fall through)."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.50  # Exactly on the boundary
        mock_confidence.reasoning = "test"

        approved, reason = engine.should_proceed_with_healing(
            mock_confidence,
            agent_name="test_agent",
            territory="test_territory",
        )

        # Should be blocked because enable_llm=False and conf <= 0.50
        assert approved is False
        assert "Manual Review Required" in reason or "LLM disabled" in reason

    def test_gemini_boundary_conf_049_blocked_when_llm_disabled(self):
        """When conf == 0.49 and enable_llm=False, should also block."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.49
        mock_confidence.reasoning = "test"

        approved, reason = engine.should_proceed_with_healing(
            mock_confidence,
            agent_name="test_agent",
            territory="test_territory",
        )

        assert approved is False
        assert "Manual Review Required" in reason or "LLM disabled" in reason

    def test_gemini_boundary_conf_051_not_blocked_when_llm_disabled(self):
        """When conf == 0.51 (above threshold) and enable_llm=False, routes to QWEN (not Gemini)."""
        from agentic_core.L0_routing.scripts.execute_ssot import AutonomousDecisionEngine

        engine = AutonomousDecisionEngine(enable_llm=False, auto_approve=False)

        mock_confidence = MagicMock()
        mock_confidence.value = 0.51  # Just above QWEN lower bound
        mock_confidence.reasoning = "test"

        # Mock Qwen to decline so we can verify it was routed there
        def mock_arbiter(*args, **kwargs):
            return {"decision": False, "reason": "Qwen declined"}

        with patch.object(engine, "_get_qwen_vllm_arbiter", return_value=mock_arbiter):
            approved, reason = engine.should_proceed_with_healing(
                mock_confidence,
                agent_name="test_agent",
                territory="test_territory",
            )

            # Should route to QWEN tier, not Gemini
            assert "QWEN14B-DECLINED" in reason or "agent logic governs" in reason
            # Should NOT have "Manual Review Required"
            assert "Manual Review Required" not in reason


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
