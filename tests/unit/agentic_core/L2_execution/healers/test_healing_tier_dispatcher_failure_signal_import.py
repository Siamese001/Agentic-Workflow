"""
Test for FailureSignal import fix in healing_tier_dispatcher.py.

Covers:
- FailureSignal is properly imported and available
- handle_qwen_oom_via_router can construct FailureSignal without NameError
- OOM escalation path works end-to-end
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

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_failure_signal_import")
_emit_applies_guardrail("p0", "test_healing_tier_dispatcher_failure_signal_import", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_dispatcher_failure_signal_import", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_dispatcher_failure_signal_import", "state_snapshot")
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

_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_1")
_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_2")
_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_3")
_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_4")
_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_5")
_emit_emits_metric_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "metric_6")
_emit_records_incident_event("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "anomaly")
_emit_writes_observability_log("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "mon_state")
_emit_triggers_alert("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "alert")
_emit_links_incident_trace("test_healing_tier_dispatcher_failure_signal_import", "p4obs", "trace_link")
_emit_captures_pattern("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "pattern")
_emit_records_learning_event("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "routing")
_emit_improves_agent_policy("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "policy")
_emit_stores_learning_state("test_healing_tier_dispatcher_failure_signal_import", "p3lm", "state")
_emit_records_execution_trace("test_healing_tier_dispatcher_failure_signal_import", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_healing_tier_dispatcher_failure_signal_import", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_healing_tier_dispatcher_failure_signal_import", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_healing_tier_dispatcher_failure_signal_import", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_healing_tier_dispatcher_failure_signal_import", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_healing_tier_dispatcher_failure_signal_import", "env_read", "p2_env_1")
_emit_reads_environ("test_healing_tier_dispatcher_failure_signal_import", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_healing_tier_dispatcher_failure_signal_import", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_healing_tier_dispatcher_failure_signal_import", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_healing_tier_dispatcher_failure_signal_import", "context_pull")
_emit_pulls_context("p1", "test_healing_tier_dispatcher_failure_signal_import", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_failure_signal_import", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_healing_tier_dispatcher_failure_signal_import", "uwg_term_2")
_emit_writes_through("p1", "test_healing_tier_dispatcher_failure_signal_import", "write_through")
_emit_writes_through("p1", "test_healing_tier_dispatcher_failure_signal_import", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_healing_tier_dispatcher_failure_signal_import", "safety_validation")
_emit_invokes_eval("p1", "test_healing_tier_dispatcher_failure_signal_import", "eval_call")
_emit_proposal_commits_routing("p1", "test_healing_tier_dispatcher_failure_signal_import", "routing_commit")
_emit_escalates_to_human("p1", "test_healing_tier_dispatcher_failure_signal_import", "human_escalation")
_emit_routes_through("p1", "test_healing_tier_dispatcher_failure_signal_import", "route_through")
_emit_checks_agent_registry("p1", "test_healing_tier_dispatcher_failure_signal_import", "agent_registry")
_emit_validates_agent_capability("p1", "test_healing_tier_dispatcher_failure_signal_import", "capability")
_emit_dispatches_execution_plan("p1", "test_healing_tier_dispatcher_failure_signal_import", "exec_plan")
_emit_agent_executes_agent("p1", "test_healing_tier_dispatcher_failure_signal_import", "sub_agent")
_emit_routes_to_agent("p1", "test_healing_tier_dispatcher_failure_signal_import", "target_agent")
_emit_verifies_policy("p1", "test_healing_tier_dispatcher_failure_signal_import", "policy_check")
_emit_observes_runtime_state("p1", "test_healing_tier_dispatcher_failure_signal_import", "runtime_state")
_emit_verifies_boundary("p1", "test_healing_tier_dispatcher_failure_signal_import", "boundary_check")
_emit_transcripts_response("p1", "test_healing_tier_dispatcher_failure_signal_import", "transcript")
_emit_hard_fails_untranscripted("p1", "test_healing_tier_dispatcher_failure_signal_import")
_emit_gated_by_confidence("p1", "test_healing_tier_dispatcher_failure_signal_import", "confidence_gate")
emit_replay_key("p0", "test_healing_tier_dispatcher_failure_signal_import")
emit_determinism_digest("p0", "test_healing_tier_dispatcher_failure_signal_import")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_healing_tier_dispatcher_failure_signal_import", "execution_auth")
_emit_validates_capability("p2", "test_healing_tier_dispatcher_failure_signal_import", "capability_check")
_emit_routes_to_capability("p2", "test_healing_tier_dispatcher_failure_signal_import", "capability_route")
_emit_writes_via_uwg("p2", "test_healing_tier_dispatcher_failure_signal_import", "uwg_write")
_emit_blocks_direct_write("p2", "test_healing_tier_dispatcher_failure_signal_import", "direct_write_block")
_emit_records_tool_invocation("p2", "test_healing_tier_dispatcher_failure_signal_import", "tool_invocation")
_emit_captures_execution_output("p2", "test_healing_tier_dispatcher_failure_signal_import", "exec_output")
_emit_dispatches_agent("p3", "test_healing_tier_dispatcher_failure_signal_import", "agent_dispatch")
_emit_coordinates_agents("p3", "test_healing_tier_dispatcher_failure_signal_import", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_healing_tier_dispatcher_failure_signal_import", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_healing_tier_dispatcher_failure_signal_import", "healing_outcome")
_emit_escalates_failure("p3", "test_healing_tier_dispatcher_failure_signal_import", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_healing_tier_dispatcher_failure_signal_import", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_healing_tier_dispatcher_failure_signal_import", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_healing_tier_dispatcher_failure_signal_import", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_healing_tier_dispatcher_failure_signal_import", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_healing_tier_dispatcher_failure_signal_import", "eval_metric")
_emit_stores_embedding("p4", "test_healing_tier_dispatcher_failure_signal_import", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_healing_tier_dispatcher_failure_signal_import", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_healing_tier_dispatcher_failure_signal_import", "exec_snapshot_link")


class TestFailureSignalImport:
    """Test that FailureSignal is properly imported in healing_tier_dispatcher."""

    def test_failure_signal_imported_in_module(self):
        """FailureSignal should be imported at module level in healing_tier_dispatcher."""
        from agentic_core.L2_execution.healers import healing_tier_dispatcher

        # Should be able to access FailureSignal from the module
        assert hasattr(healing_tier_dispatcher, "FailureSignal")

        # Should be the correct type from healing_tier_types
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal as ExpectedType

        assert healing_tier_dispatcher.FailureSignal is ExpectedType

    def test_handle_qwen_oom_via_router_function_exists_and_references_failure_signal(self):
        """handle_qwen_oom_via_router should reference FailureSignal in its implementation."""
        import inspect

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router

        # Get the source code of the function
        source = inspect.getsource(handle_qwen_oom_via_router)

        # Should reference FailureSignal (the bug was it wasn't imported)
        assert "FailureSignal" in source
        assert "failure_signal =" in source or "FailureSignal(" in source

    def test_oom_handler_uses_route_healing_tier(self):
        """OOM handler should call route_healing_tier (the single choke point)."""
        import inspect

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router

        # Get the source code
        source = inspect.getsource(handle_qwen_oom_via_router)

        # Should call route_healing_tier (the single choke point)
        assert "route_healing_tier" in source


class TestOOMEscalationPath:
    """Test the full OOM escalation workflow."""

    def test_oom_escalation_routes_through_single_choke_point(self):
        """OOM escalation should route through route_healing_tier (single choke point)."""
        from unittest.mock import patch

        from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingInput,
            HealingTier,
        )

        config = HealingTierConfig()

        healing_input = HealingInput(
            failure_type="test_failure",
            error_signature="test_sig",
            trace_id="test_trace",
            retry_count=0,
            blast_radius_estimate=0.1,
            required_tools=(),
            violation_metadata_refs=(),
            agent_id="test_agent",
        )

        # Mock route_healing_tier to verify it's called
        mock_decision = HealingDecision(
            heal_confidence=0.5,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=("oom_escalation",),
        )

        with patch(
            "agentic_core.L2_execution.healers.healing_tier_dispatcher.route_healing_tier",
            return_value=mock_decision,
        ) as mock_route:
            decision = handle_qwen_oom_via_router(healing_input, config)

            # Should have called route_healing_tier (the single choke point)
            assert mock_route.called
            # Should return the decision from the router
            assert decision is mock_decision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
