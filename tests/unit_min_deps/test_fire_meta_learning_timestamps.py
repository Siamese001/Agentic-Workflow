"""GAP-A: _fire_meta_learning_intake must use injected now_utc, never timestamp_utc=0."""

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_fire_meta_learning_timestamps")
# REMOVED: _emit_applies_guardrail("p0", "test_fire_meta_learning_timestamps", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_fire_meta_learning_timestamps", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_fire_meta_learning_timestamps", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_fire_meta_learning_timestamps", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_fire_meta_learning_timestamps", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_fire_meta_learning_timestamps", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_fire_meta_learning_timestamps", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_fire_meta_learning_timestamps", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_fire_meta_learning_timestamps", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_fire_meta_learning_timestamps", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_fire_meta_learning_timestamps", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_fire_meta_learning_timestamps", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_fire_meta_learning_timestamps", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_fire_meta_learning_timestamps", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_fire_meta_learning_timestamps", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_fire_meta_learning_timestamps", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_fire_meta_learning_timestamps", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_fire_meta_learning_timestamps", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_fire_meta_learning_timestamps", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_fire_meta_learning_timestamps", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_fire_meta_learning_timestamps", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_fire_meta_learning_timestamps", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_fire_meta_learning_timestamps", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_fire_meta_learning_timestamps", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_fire_meta_learning_timestamps", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_fire_meta_learning_timestamps", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_fire_meta_learning_timestamps", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_fire_meta_learning_timestamps", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_fire_meta_learning_timestamps", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_fire_meta_learning_timestamps", "write_through")
# REMOVED: _emit_writes_through("p1", "test_fire_meta_learning_timestamps", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_fire_meta_learning_timestamps", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_fire_meta_learning_timestamps", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_fire_meta_learning_timestamps", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_fire_meta_learning_timestamps", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_fire_meta_learning_timestamps", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_fire_meta_learning_timestamps", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_fire_meta_learning_timestamps", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_fire_meta_learning_timestamps", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_fire_meta_learning_timestamps", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_fire_meta_learning_timestamps", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_fire_meta_learning_timestamps", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_fire_meta_learning_timestamps", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_fire_meta_learning_timestamps", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_fire_meta_learning_timestamps", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_fire_meta_learning_timestamps")
# REMOVED: _emit_gated_by_confidence("p1", "test_fire_meta_learning_timestamps", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_fire_meta_learning_timestamps")
# REMOVED: emit_determinism_digest("p0", "test_fire_meta_learning_timestamps")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_fire_meta_learning_timestamps", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_fire_meta_learning_timestamps", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_fire_meta_learning_timestamps", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_fire_meta_learning_timestamps", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_fire_meta_learning_timestamps", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_fire_meta_learning_timestamps", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_fire_meta_learning_timestamps", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_fire_meta_learning_timestamps", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_fire_meta_learning_timestamps", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_fire_meta_learning_timestamps", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_fire_meta_learning_timestamps", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_fire_meta_learning_timestamps", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_fire_meta_learning_timestamps", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_fire_meta_learning_timestamps", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_fire_meta_learning_timestamps", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_fire_meta_learning_timestamps", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_fire_meta_learning_timestamps", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_fire_meta_learning_timestamps", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_fire_meta_learning_timestamps", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_fire_meta_learning_timestamps", "exec_snapshot_link")

EXECUTE_SSOT_PATH = Path(__file__).parent.parent.parent / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"


@pytest.mark.unit_min_deps
class TestFireMetaLearningTimestamps:
    def _make_state_mgr(self, healing_actions=None):
        mgr = MagicMock()
        state = {
            "healing_actions": healing_actions or [],
            "meta_learning": {},
            "apply_proposals": False,
        }
        mgr.state = state
        mgr.update_meta_learning = MagicMock()
        return mgr

    def test_signature_accepts_now_utc_parameter(self):
        """_fire_meta_learning_intake must accept now_utc as a parameter (not read wall-clock internally)."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                args = [a.arg for a in node.args.args]
                assert "now_utc" in args, "_fire_meta_learning_intake must declare now_utc parameter"
                return
        pytest.fail("_fire_meta_learning_intake not found in execute_ssot.py")

    def test_no_hardcoded_zero_timestamps_in_source(self):
        """AST: no timestamp_utc=0 or created_utc=0 literals remain in _fire_meta_learning_intake."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)

        # Find _fire_meta_learning_intake function node
        fn_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                fn_node = node
                break
        assert fn_node is not None

        # Walk all keyword arguments within that function
        for node in ast.walk(fn_node):
            if isinstance(node, ast.keyword):
                if node.arg in ("timestamp_utc", "created_utc"):
                    # Must not be a literal 0
                    if isinstance(node.value, ast.Constant) and node.value.value == 0:
                        pytest.fail(f"Hardcoded {node.arg}=0 found in _fire_meta_learning_intake")

    def test_created_utc_in_jsonl_not_zero(self):
        """Wave 2 JSONL lines must not contain created_utc: 0 literal in source."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
        fn_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_fire_meta_learning_intake":
                fn_node = node
                break
        assert fn_node is not None

        for node in ast.walk(fn_node):
            if isinstance(node, ast.Dict):
                for key, val in zip(node.keys, node.values):
                    if isinstance(key, ast.Constant) and key.value == "created_utc":
                        if isinstance(val, ast.Constant) and val.value == 0:
                            pytest.fail("Dict literal 'created_utc': 0 found in _fire_meta_learning_intake")

    def test_empty_healing_actions_no_crash(self):
    """Test empty_healing_actions_no_crash runtime behavior."""
    # Arrange
    # TODO: Set up test data for empty_healing_actions_no_crash
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute empty_healing_actions_no_crash
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        injected_ts = 9_000_000

        aggregator = HealingOutcomeAggregator(window_size=1)
        aggregator.ingest(
            HealingOutcomeEvent(
                healer_id="agent_x",
                tier="L5",
                failure_type="TYPE_A",
                success=True,
                timestamp_utc=injected_ts,
            )
        )
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        record = adapter.build_record(aggregator=aggregator, created_utc=injected_ts, source="test")
        adapter.persist_record(record)

        assert store.count() == 1
        assert store.get_records()[0].created_utc == injected_ts
        assert store.get_records()[0].created_utc != 0

    def test_determinism_same_input_same_bytes(self):
        """Same now_utc + same healing event → identical canonical_bytes() across two calls."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        fixed_ts = 5_000_000

        def make_record():
            agg = HealingOutcomeAggregator(window_size=1)
            agg.ingest(
                HealingOutcomeEvent(
                    healer_id="det_agent",
                    tier="L0",
                    failure_type="DET_FAIL",
                    success=False,
                    timestamp_utc=fixed_ts,
                )
            )
            store = InMemoryHealingOutcomeIntakeStore()
            adapter = HealingOutcomeIntakeAdapter(store=store)
            rec = adapter.build_record(aggregator=agg, created_utc=fixed_ts, source="test")
            return rec.canonical_bytes()

        assert make_record() == make_record()

    def test_boundary_single_healing_action(self):
    """Test boundary_single_healing_action runtime behavior."""
    # Arrange
    # TODO: Set up test data for boundary_single_healing_action
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Execute boundary_single_healing_action
    result = None  # Replace with actual function call

    # Assert
    assert result is not None, f"{function_name} should return a result"
    assert isinstance(result, object), "Result should be an object"
    # TODO: Add specific runtime behavior assertions
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        rec = adapter.build_record(aggregator=agg, created_utc=ts, source="test")
        adapter.persist_record(rec)

        assert store.count() == 1
        assert store.get_records()[0].created_utc == ts
        assert store.get_records()[0].created_utc != 0
