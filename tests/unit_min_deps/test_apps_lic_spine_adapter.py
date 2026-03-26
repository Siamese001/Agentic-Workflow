"""Tests for LIC spine adapter — deterministic CID + spine routing."""

from unittest.mock import MagicMock, patch

import pytest

#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_authorize_and_execute("p2", "test_apps_lic_spine_adapter", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_apps_lic_spine_adapter", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_apps_lic_spine_adapter", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_apps_lic_spine_adapter", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_apps_lic_spine_adapter", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_apps_lic_spine_adapter", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_apps_lic_spine_adapter", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_apps_lic_spine_adapter", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_apps_lic_spine_adapter", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_apps_lic_spine_adapter", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_apps_lic_spine_adapter", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_apps_lic_spine_adapter", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_apps_lic_spine_adapter", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_apps_lic_spine_adapter", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_apps_lic_spine_adapter", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_apps_lic_spine_adapter", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_apps_lic_spine_adapter", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_apps_lic_spine_adapter", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_apps_lic_spine_adapter", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_apps_lic_spine_adapter", "exec_snapshot_link")
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter

# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_apps_lic_spine_adapter", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_apps_lic_spine_adapter", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_apps_lic_spine_adapter", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_apps_lic_spine_adapter", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_apps_lic_spine_adapter", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_apps_lic_spine_adapter", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_apps_lic_spine_adapter", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_apps_lic_spine_adapter", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_apps_lic_spine_adapter", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_apps_lic_spine_adapter", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_apps_lic_spine_adapter", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_apps_lic_spine_adapter", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_apps_lic_spine_adapter", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_apps_lic_spine_adapter", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_apps_lic_spine_adapter", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_apps_lic_spine_adapter", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_apps_lic_spine_adapter", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_apps_lic_spine_adapter", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_apps_lic_spine_adapter", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_apps_lic_spine_adapter", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_apps_lic_spine_adapter", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_apps_lic_spine_adapter", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_apps_lic_spine_adapter", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_apps_lic_spine_adapter")
# REMOVED: _emit_applies_guardrail("p0", "test_apps_lic_spine_adapter", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_apps_lic_spine_adapter", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_apps_lic_spine_adapter", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_apps_lic_spine_adapter", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_apps_lic_spine_adapter", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_apps_lic_spine_adapter", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_apps_lic_spine_adapter", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_apps_lic_spine_adapter", "write_through")
# REMOVED: _emit_writes_through("p1", "test_apps_lic_spine_adapter", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_apps_lic_spine_adapter", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_apps_lic_spine_adapter", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_apps_lic_spine_adapter", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_apps_lic_spine_adapter", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_apps_lic_spine_adapter", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_apps_lic_spine_adapter", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_apps_lic_spine_adapter", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_apps_lic_spine_adapter", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_apps_lic_spine_adapter", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_apps_lic_spine_adapter", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_apps_lic_spine_adapter", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_apps_lic_spine_adapter", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_apps_lic_spine_adapter", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_apps_lic_spine_adapter", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_apps_lic_spine_adapter")
# REMOVED: _emit_gated_by_confidence("p1", "test_apps_lic_spine_adapter", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_apps_lic_spine_adapter")
# REMOVED: emit_determinism_digest("p0", "test_apps_lic_spine_adapter")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

@pytest.mark.unit_min_deps
def test_adapter_returns_cid():
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    """Adapter returns a cid in result."""
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert "cid" in result
        assert result["cid"].startswith("lic-")
        assert len(result["cid"]) == 20  # "lic-" + 16 char hash


@pytest.mark.unit_min_deps
def test_cid_has_lic_prefix():
    """CID has 'lic-' prefix."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result = adapter.execute({"s0_system": "test"})

        assert result["cid"].startswith("lic-")


@pytest.mark.unit_min_deps
def test_cid_is_deterministic():
    """Calling adapter twice with identical intent_input produces same cid."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        result1 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})
        result2 = adapter.execute({"s0_system": "test", "i0_instructional": "instruction"})

        assert result1["cid"] == result2["cid"]


@pytest.mark.unit_min_deps
def test_different_inputs_produce_different_cids():
    """Different intent_inputs produce different cids."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        def fresh_result(*args, **kwargs):
            return {"status": "ok"}

        mock_orch.return_value.execute = fresh_result

        adapter1 = LicSpineAdapter()
        result1 = adapter1.execute({"s0_system": "test1", "i0_instructional": "instruction1"})

        adapter2 = LicSpineAdapter()
        result2 = adapter2.execute({"s0_system": "test2", "i0_instructional": "instruction2"})

        assert result1["cid"] != result2["cid"]


@pytest.mark.unit_min_deps
def test_cid_registered_before_orchestrator_execute():
    """CIDRegistry.new_cycle called before ExecutionOrchestrator.execute."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = LicSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify call order
            mock_registry.return_value.new_cycle.assert_called_once()
            mock_orch.return_value.execute.assert_called_once()

            # Get the cid passed to new_cycle
            cid_arg = mock_registry.return_value.new_cycle.call_args[0][0]
            assert cid_arg.startswith("lic-")

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert enriched_input["_cid"] == cid_arg


@pytest.mark.unit_min_deps
def test_cid_passed_to_orchestrator():
    """CID is passed to orchestrator in enriched intent_input."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        with patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_registry:
            mock_cycle = MagicMock()
            mock_cycle.attempt = 1
            mock_registry.return_value.new_cycle.return_value = mock_cycle
            mock_orch.return_value.execute.return_value = {"status": "ok"}

            adapter = LicSpineAdapter()
            adapter.execute({"s0_system": "test"})

            # Verify orchestrator received enriched input
            enriched_input = mock_orch.return_value.execute.call_args[0][0]
            assert "_cid" in enriched_input
            assert "_cycle_attempt" in enriched_input
            assert enriched_input["_cycle_attempt"] == 1


@pytest.mark.unit_min_deps
def test_adapter_state_success_on_clean_input():
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    """Adapter succeeds on clean input without side effects."""
#  # MOVED: from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
    with patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_orch:
        # Return a fresh dict each time to avoid mutation
        mock_orch.return_value.execute.return_value = {"status": "ok"}

        adapter = LicSpineAdapter()
        # Should not raise
        result = adapter.execute(
            {
                "s0_system": "test_system",
                "i0_instructional": "test_instruction",
                "c0_context": "test_context",
                "u0_user_prompt": "test_prompt",
                "d0_injections": "test_injection",
            }
        )

        assert result["status"] == "ok"
        assert "cid" in result
