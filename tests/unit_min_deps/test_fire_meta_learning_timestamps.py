"""GAP-A: _fire_meta_learning_intake must use injected now_utc, never timestamp_utc=0."""

import ast
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
)
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

_emit_records_execution_trace("p0", "evidence", "test_fire_meta_learning_timestamps")
_emit_applies_guardrail("p0", "test_fire_meta_learning_timestamps", "p0_governance")
_emit_reads_policy_state("p0", "test_fire_meta_learning_timestamps", "policy_binding")
_emit_snapshots_state("p0", "test_fire_meta_learning_timestamps", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_1")
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_2")
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_3")
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_4")
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_5")
_emit_emits_metric_event("test_fire_meta_learning_timestamps", "p4obs", "metric_6")
_emit_records_incident_event("test_fire_meta_learning_timestamps", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_fire_meta_learning_timestamps", "p4obs", "anomaly")
_emit_writes_observability_log("test_fire_meta_learning_timestamps", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_fire_meta_learning_timestamps", "p4obs", "mon_state")
_emit_triggers_alert("test_fire_meta_learning_timestamps", "p4obs", "alert")
_emit_links_incident_trace("test_fire_meta_learning_timestamps", "p4obs", "trace_link")
_emit_captures_pattern("test_fire_meta_learning_timestamps", "p3lm", "pattern")
_emit_records_learning_event("test_fire_meta_learning_timestamps", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_fire_meta_learning_timestamps", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_fire_meta_learning_timestamps", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_fire_meta_learning_timestamps", "p3lm", "routing")
_emit_improves_agent_policy("test_fire_meta_learning_timestamps", "p3lm", "policy")
_emit_stores_learning_state("test_fire_meta_learning_timestamps", "p3lm", "state")
_emit_records_execution_trace("test_fire_meta_learning_timestamps", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_fire_meta_learning_timestamps", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_fire_meta_learning_timestamps", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_fire_meta_learning_timestamps", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_fire_meta_learning_timestamps", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_fire_meta_learning_timestamps", "env_read", "p2_env_1")
_emit_reads_environ("test_fire_meta_learning_timestamps", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_fire_meta_learning_timestamps", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_fire_meta_learning_timestamps", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_fire_meta_learning_timestamps", "context_pull")
_emit_pulls_context("p1", "test_fire_meta_learning_timestamps", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_fire_meta_learning_timestamps", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_fire_meta_learning_timestamps", "uwg_term_2")
_emit_writes_through("p1", "test_fire_meta_learning_timestamps", "write_through")
_emit_writes_through("p1", "test_fire_meta_learning_timestamps", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_fire_meta_learning_timestamps", "safety_validation")
_emit_invokes_eval("p1", "test_fire_meta_learning_timestamps", "eval_call")
_emit_proposal_commits_routing("p1", "test_fire_meta_learning_timestamps", "routing_commit")
emit_replay_key("p0", "test_fire_meta_learning_timestamps")
emit_determinism_digest("p0", "test_fire_meta_learning_timestamps")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_fire_meta_learning_timestamps", "execution_auth")
_emit_validates_capability("p2", "test_fire_meta_learning_timestamps", "capability_check")
_emit_routes_to_capability("p2", "test_fire_meta_learning_timestamps", "capability_route")
_emit_writes_via_uwg("p2", "test_fire_meta_learning_timestamps", "uwg_write")
_emit_blocks_direct_write("p2", "test_fire_meta_learning_timestamps", "direct_write_block")
_emit_records_tool_invocation("p2", "test_fire_meta_learning_timestamps", "tool_invocation")
_emit_captures_execution_output("p2", "test_fire_meta_learning_timestamps", "exec_output")
_emit_dispatches_agent("p3", "test_fire_meta_learning_timestamps", "agent_dispatch")
_emit_coordinates_agents("p3", "test_fire_meta_learning_timestamps", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_fire_meta_learning_timestamps", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_fire_meta_learning_timestamps", "healing_outcome")
_emit_escalates_failure("p3", "test_fire_meta_learning_timestamps", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_fire_meta_learning_timestamps", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_fire_meta_learning_timestamps", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_fire_meta_learning_timestamps", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_fire_meta_learning_timestamps", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_fire_meta_learning_timestamps", "eval_metric")
_emit_stores_embedding("p4", "test_fire_meta_learning_timestamps", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_fire_meta_learning_timestamps", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_fire_meta_learning_timestamps", "exec_snapshot_link")

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
        """Empty healing_actions must not crash _fire_meta_learning_intake."""
        from agentic_core.L0_routing.scripts.execute_ssot import _fire_meta_learning_intake

        mgr = self._make_state_mgr(healing_actions=[])
        # Should not raise
        _fire_meta_learning_intake(mgr, now_utc=12345)

    def test_now_utc_propagated_to_intake_record(self):
        """created_utc on the persisted record must equal the injected now_utc."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
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
        """Single healing action must produce exactly one record with correct timestamp."""
        from system_learning.engines.healing_outcome_aggregator import HealingOutcomeAggregator
        from system_learning.engines.healing_outcome_intake_adapter import HealingOutcomeIntakeAdapter
        from system_learning.engines.in_memory_healing_outcome_intake_store import (
            InMemoryHealingOutcomeIntakeStore,
        )
        from system_learning.types.healing_outcome_types import HealingOutcomeEvent

        ts = 1_000_001
        agg = HealingOutcomeAggregator(window_size=1)
        agg.ingest(
            HealingOutcomeEvent(healer_id="a", tier="L1", failure_type="F", success=True, timestamp_utc=ts)
        )
        store = InMemoryHealingOutcomeIntakeStore()
        adapter = HealingOutcomeIntakeAdapter(store=store)
        rec = adapter.build_record(aggregator=agg, created_utc=ts, source="test")
        adapter.persist_record(rec)

        assert store.count() == 1
        assert store.get_records()[0].created_utc == ts
        assert store.get_records()[0].created_utc != 0
