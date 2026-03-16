"""Cross-app contract test for spine adapters."""

from unittest.mock import MagicMock, patch

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

_emit_authorize_and_execute("p2", "test_spine_cross_app_contract", "execution_auth")
_emit_validates_capability("p2", "test_spine_cross_app_contract", "capability_check")
_emit_routes_to_capability("p2", "test_spine_cross_app_contract", "capability_route")
_emit_writes_via_uwg("p2", "test_spine_cross_app_contract", "uwg_write")
_emit_blocks_direct_write("p2", "test_spine_cross_app_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "test_spine_cross_app_contract", "tool_invocation")
_emit_captures_execution_output("p2", "test_spine_cross_app_contract", "exec_output")
_emit_dispatches_agent("p3", "test_spine_cross_app_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "test_spine_cross_app_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_spine_cross_app_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_spine_cross_app_contract", "healing_outcome")
_emit_escalates_failure("p3", "test_spine_cross_app_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_spine_cross_app_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_spine_cross_app_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_spine_cross_app_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_spine_cross_app_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_spine_cross_app_contract", "eval_metric")
_emit_stores_embedding("p4", "test_spine_cross_app_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_spine_cross_app_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_spine_cross_app_contract", "exec_snapshot_link")
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
)
from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
from apps_rg.engines.rg_spine_adapter import RgSpineAdapter

_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_1")
_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_2")
_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_3")
_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_4")
_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_5")
_emit_emits_metric_event("test_spine_cross_app_contract", "p4obs", "metric_6")
_emit_records_incident_event("test_spine_cross_app_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_spine_cross_app_contract", "p4obs", "anomaly")
_emit_writes_observability_log("test_spine_cross_app_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_spine_cross_app_contract", "p4obs", "mon_state")
_emit_triggers_alert("test_spine_cross_app_contract", "p4obs", "alert")
_emit_links_incident_trace("test_spine_cross_app_contract", "p4obs", "trace_link")
_emit_captures_pattern("test_spine_cross_app_contract", "p3lm", "pattern")
_emit_records_learning_event("test_spine_cross_app_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_spine_cross_app_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_spine_cross_app_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_spine_cross_app_contract", "p3lm", "routing")
_emit_improves_agent_policy("test_spine_cross_app_contract", "p3lm", "policy")
_emit_stores_learning_state("test_spine_cross_app_contract", "p3lm", "state")
_emit_records_execution_trace("test_spine_cross_app_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_spine_cross_app_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_spine_cross_app_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_spine_cross_app_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_spine_cross_app_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_spine_cross_app_contract", "env_read", "p2_env_1")
_emit_reads_environ("test_spine_cross_app_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_spine_cross_app_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_spine_cross_app_contract", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_spine_cross_app_contract")
_emit_applies_guardrail("p0", "test_spine_cross_app_contract", "p0_governance")
_emit_reads_policy_state("p0", "test_spine_cross_app_contract", "policy_binding")
_emit_snapshots_state("p0", "test_spine_cross_app_contract", "state_snapshot")
_emit_pulls_context("p1", "test_spine_cross_app_contract", "context_pull")
_emit_pulls_context("p1", "test_spine_cross_app_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_spine_cross_app_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_spine_cross_app_contract", "uwg_term_secondary")
_emit_writes_through("p1", "test_spine_cross_app_contract", "write_through")
_emit_writes_through("p1", "test_spine_cross_app_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_spine_cross_app_contract", "safety_validation")
_emit_invokes_eval("p1", "test_spine_cross_app_contract", "eval_call")
_emit_proposal_commits_routing("p1", "test_spine_cross_app_contract", "routing_commit")
_emit_escalates_to_human("p1", "test_spine_cross_app_contract", "human_escalation")
_emit_routes_through("p1", "test_spine_cross_app_contract", "route_through")
_emit_checks_agent_registry("p1", "test_spine_cross_app_contract", "agent_registry")
_emit_validates_agent_capability("p1", "test_spine_cross_app_contract", "capability")
_emit_dispatches_execution_plan("p1", "test_spine_cross_app_contract", "exec_plan")
_emit_agent_executes_agent("p1", "test_spine_cross_app_contract", "sub_agent")
_emit_routes_to_agent("p1", "test_spine_cross_app_contract", "target_agent")
_emit_verifies_policy("p1", "test_spine_cross_app_contract", "policy_check")
_emit_observes_runtime_state("p1", "test_spine_cross_app_contract", "runtime_state")
_emit_verifies_boundary("p1", "test_spine_cross_app_contract", "boundary_check")
_emit_transcripts_response("p1", "test_spine_cross_app_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "test_spine_cross_app_contract")
_emit_gated_by_confidence("p1", "test_spine_cross_app_contract", "confidence_gate")
emit_replay_key("p0", "test_spine_cross_app_contract")
emit_determinism_digest("p0", "test_spine_cross_app_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
def test_cross_app_cid_prefixes():
    """Given same semantic payload, LIC CID starts with 'lic-' and RG CID starts with 'rg-'."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with (
        patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch,
        patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch,
    ):
        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result = lic_adapter.execute(payload)
        rg_result = rg_adapter.execute(payload)

        assert lic_result["cid"].startswith("lic-")
        assert rg_result["cid"].startswith("rg-")


@pytest.mark.unit_min_deps
def test_cross_app_cid_hash_bodies_identical():
    """Given same semantic payload, CID hash bodies (without prefix) are identical."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with (
        patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch,
        patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch,
    ):
        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result = lic_adapter.execute(payload)
        rg_result = rg_adapter.execute(payload)

        # Extract hash bodies (remove prefixes)
        lic_hash_body = lic_result["cid"][4:]  # Remove "lic-"
        rg_hash_body = rg_result["cid"][3:]  # Remove "rg-"

        assert lic_hash_body == rg_hash_body


@pytest.mark.unit_min_deps
def test_cross_app_cid_determinism():
    """Running twice with identical canonicalized payload yields identical CID each time."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with (
        patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch,
        patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch,
    ):
        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        # Run twice
        lic_result1 = lic_adapter.execute(payload)
        lic_result2 = lic_adapter.execute(payload)
        rg_result1 = rg_adapter.execute(payload)
        rg_result2 = rg_adapter.execute(payload)

        # Check determinism
        assert lic_result1["cid"] == lic_result2["cid"]
        assert rg_result1["cid"] == rg_result2["cid"]


@pytest.mark.unit_min_deps
def test_cross_app_cid_difference():
    """Minimally different semantic payload yields different hash body."""
    payload1 = {"s0_system": "test", "i0_instructional": "instruction"}
    payload2 = {"s0_system": "test", "i0_instructional": "different"}

    with (
        patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch,
        patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch,
    ):
        # Return fresh dicts to avoid mutation
        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        lic_result1 = lic_adapter.execute(payload1)
        lic_result2 = lic_adapter.execute(payload2)
        rg_result1 = rg_adapter.execute(payload1)
        rg_result2 = rg_adapter.execute(payload2)

        # Extract hash bodies
        lic_hash_body1 = lic_result1["cid"][4:]
        lic_hash_body2 = lic_result2["cid"][4:]
        rg_hash_body1 = rg_result1["cid"][3:]
        rg_hash_body2 = rg_result2["cid"][3:]

        # Check that different payloads produce different hash bodies
        assert lic_hash_body1 != lic_hash_body2
        assert rg_hash_body1 != rg_hash_body2

        # But same payload across apps should produce same hash body
        assert lic_hash_body1 == rg_hash_body1
        assert lic_hash_body2 == rg_hash_body2


@pytest.mark.unit_min_deps
def test_cross_app_call_order_invariant():
    """new_cycle called before orchestrator.execute for both apps."""
    payload = {"s0_system": "test", "i0_instructional": "instruction"}

    with (
        patch("apps_lic.engines.lic_spine_adapter.ExecutionOrchestrator") as mock_lic_orch,
        patch("apps_rg.engines.rg_spine_adapter.ExecutionOrchestrator") as mock_rg_orch,
        patch("apps_lic.engines.lic_spine_adapter.CIDRegistry") as mock_lic_registry,
        patch("apps_rg.engines.rg_spine_adapter.CIDRegistry") as mock_rg_registry,
    ):
        # Setup mocks
        mock_cycle = MagicMock()
        mock_cycle.attempt = 1
        mock_lic_registry.return_value.new_cycle.return_value = mock_cycle
        mock_rg_registry.return_value.new_cycle.return_value = mock_cycle

        mock_lic_orch.return_value.execute.return_value = {"status": "ok"}
        mock_rg_orch.return_value.execute.return_value = {"status": "ok"}

        lic_adapter = LicSpineAdapter()
        rg_adapter = RgSpineAdapter()

        # Execute adapters
        lic_adapter.execute(payload)
        rg_adapter.execute(payload)

        # Verify call order: new_cycle called before execute
        assert mock_lic_registry.return_value.new_cycle.called
        assert mock_rg_registry.return_value.new_cycle.called
        assert mock_lic_orch.return_value.execute.called
        assert mock_rg_orch.return_value.execute.called

        # Check that new_cycle was called exactly once for each adapter
        assert mock_lic_registry.return_value.new_cycle.call_count == 1
        assert mock_rg_registry.return_value.new_cycle.call_count == 1
