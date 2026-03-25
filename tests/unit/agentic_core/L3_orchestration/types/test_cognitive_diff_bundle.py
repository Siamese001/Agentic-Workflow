"""
§Wave4.2 — L3CognitiveDiffBundle tests.

1. Contract/serialization: stable JSON, sorted diff ops
2. SemanticClock enforcement: None → ValueError
3. Determinism/idempotency: same inputs → identical JSON + trace_id
4. Integration seam: before/after snapshots → expected diff ops
"""

from __future__ import annotations

import json

import pytest

from agentic_core.L0_routing.types.determinism_types import SemanticClockSnapshot
from agentic_core.L3_orchestration.types.cognitive_diff_types import (
    CognitiveStateSnapshot,
    DiffOp,
    L3CognitiveDiffBundle,
    compute_cognitive_diff,
    emit_cognitive_diff_bundle,
)
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
)

# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_cognitive_diff_bundle", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_cognitive_diff_bundle", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_cognitive_diff_bundle", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_cognitive_diff_bundle", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_cognitive_diff_bundle", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_cognitive_diff_bundle", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_cognitive_diff_bundle", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_cognitive_diff_bundle", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_cognitive_diff_bundle", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_cognitive_diff_bundle", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_cognitive_diff_bundle", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_cognitive_diff_bundle", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_cognitive_diff_bundle", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_cognitive_diff_bundle", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_cognitive_diff_bundle", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_cognitive_diff_bundle", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_cognitive_diff_bundle", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_cognitive_diff_bundle", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_cognitive_diff_bundle", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_cognitive_diff_bundle", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_cognitive_diff_bundle", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_cognitive_diff_bundle", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_cognitive_diff_bundle", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_cognitive_diff_bundle")
# REMOVED: _emit_applies_guardrail("p0", "test_cognitive_diff_bundle", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_cognitive_diff_bundle", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_cognitive_diff_bundle", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_cognitive_diff_bundle", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_cognitive_diff_bundle", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_cognitive_diff_bundle", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_cognitive_diff_bundle", "write_through")
# REMOVED: _emit_writes_through("p1", "test_cognitive_diff_bundle", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_cognitive_diff_bundle", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_cognitive_diff_bundle", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_cognitive_diff_bundle", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_cognitive_diff_bundle", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_cognitive_diff_bundle", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_cognitive_diff_bundle", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_cognitive_diff_bundle", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_cognitive_diff_bundle", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_cognitive_diff_bundle", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_cognitive_diff_bundle", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_cognitive_diff_bundle", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_cognitive_diff_bundle", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_cognitive_diff_bundle", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_cognitive_diff_bundle", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_cognitive_diff_bundle")
# REMOVED: _emit_gated_by_confidence("p1", "test_cognitive_diff_bundle", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_cognitive_diff_bundle")
# REMOVED: emit_determinism_digest("p0", "test_cognitive_diff_bundle")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_cognitive_diff_bundle", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_cognitive_diff_bundle", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_cognitive_diff_bundle", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_cognitive_diff_bundle", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_cognitive_diff_bundle", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_cognitive_diff_bundle", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_cognitive_diff_bundle", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_cognitive_diff_bundle", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_cognitive_diff_bundle", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_cognitive_diff_bundle", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_cognitive_diff_bundle", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_cognitive_diff_bundle", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_cognitive_diff_bundle", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_cognitive_diff_bundle", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_cognitive_diff_bundle", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_cognitive_diff_bundle", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_cognitive_diff_bundle", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_cognitive_diff_bundle", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_cognitive_diff_bundle", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_cognitive_diff_bundle", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def clock() -> SemanticClockSnapshot:
    return SemanticClockSnapshot(tick=7, vector_clock=(("L0", 3), ("L3", 4)))


@pytest.fixture
def before_state() -> CognitiveStateSnapshot:
    return CognitiveStateSnapshot(
        route_context="user_request_heal",
        candidate_paths=("human_escalation", "low_risk_bypass", "standard_validation"),
        selected_path="",
        rationale_enum="pending",
        risk_score=0.0,
        budget_est=0.0,
    )


@pytest.fixture
def after_state() -> CognitiveStateSnapshot:
    return CognitiveStateSnapshot(
        route_context="user_request_heal",
        candidate_paths=("human_escalation", "low_risk_bypass", "standard_validation"),
        selected_path="standard_validation",
        rationale_enum="low_risk_deterministic",
        risk_score=0.15,
        budget_est=0.3,
    )


# ===========================================================================
# 1. Contract / serialization
# ===========================================================================


class TestContractSerialization:
    def test_to_dict_stable_json(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        j = json.dumps(bundle.to_dict(), sort_keys=True, separators=(",", ":"))
        assert isinstance(j, str)
        parsed = json.loads(j)
        assert parsed["artifact_type"] == "COGNITIVE_DIFF_BUNDLE"
        assert parsed["semantic_clock"]["tick"] == 7

    def test_diff_ops_sorted_by_path(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        paths = [op.path for op in bundle.diff]
        assert paths == sorted(paths)

    def test_to_dict_has_all_top_level_keys(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        d = bundle.to_dict()
        assert set(d.keys()) == {
            "artifact_type",
            "semantic_clock",
            "trace_id",
            "before",
            "after",
            "diff",
            "policy_config_hash",
        }

    def test_frozen_immutable(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        with pytest.raises(AttributeError):
            bundle.trace_id = "mutated"  # type: ignore[misc]

    def test_wrong_artifact_type_raises(self, clock, before_state, after_state):
        with pytest.raises(ValueError, match="artifact_type must be"):
            L3CognitiveDiffBundle(
                artifact_type="WRONG",
                semantic_clock=clock,
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(),
            )

    def test_unsorted_diff_raises(self, clock, before_state, after_state):
        with pytest.raises(ValueError, match="diff ops must be sorted"):
            L3CognitiveDiffBundle(
                artifact_type="COGNITIVE_DIFF_BUNDLE",
                semantic_clock=clock,
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(
                    DiffOp(path="z_field", before="a", after="b"),
                    DiffOp(path="a_field", before="x", after="y"),
                ),
            )


# ===========================================================================
# 2. SemanticClock enforcement
# ===========================================================================


class TestSemanticClockEnforcement:
    def test_none_semantic_clock_raises_on_bundle(self, before_state, after_state):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            L3CognitiveDiffBundle(
                artifact_type="COGNITIVE_DIFF_BUNDLE",
                semantic_clock=None,  # type: ignore[arg-type]
                trace_id="t1",
                before=before_state,
                after=after_state,
                diff=(),
            )

    def test_none_semantic_clock_raises_on_emit(self, before_state, after_state):
        with pytest.raises(ValueError, match="semantic_clock is required"):
            emit_cognitive_diff_bundle(
                before=before_state,
                after=after_state,
                semantic_clock=None,  # type: ignore[arg-type]
            )


# ===========================================================================
# 3. Determinism / idempotency
# ===========================================================================


class TestDeterminismIdempotency:
    def test_same_inputs_byte_identical_json(
        self,
        clock,
        before_state,
        after_state,
    ):
        def _make():
            return emit_cognitive_diff_bundle(
                before=before_state,
                after=after_state,
                semantic_clock=clock,
                policy_config_hash="hash_abc",
            )

        j1 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        j2 = json.dumps(_make().to_dict(), sort_keys=True, separators=(",", ":"))
        assert j1 == j2

    def test_trace_id_deterministic_across_calls(
        self,
        clock,
        before_state,
        after_state,
    ):
        a = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        b = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        assert a.trace_id == b.trace_id

    def test_different_tick_different_trace_id(self, before_state, after_state):
        c1 = SemanticClockSnapshot(tick=1)
        c2 = SemanticClockSnapshot(tick=2)
        a = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=c1,
        )
        b = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=c2,
        )
        assert a.trace_id != b.trace_id

    def test_no_diff_produces_empty_ops(self, clock, before_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=before_state,
            semantic_clock=clock,
        )
        assert bundle.diff == ()


# ===========================================================================
# 4. Integration seam: before/after → expected diff ops
# ===========================================================================


class TestIntegrationSeam:
    def test_changed_fields_produce_diff_ops(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        diff_paths = {op.path for op in diff}
        assert "selected_path" in diff_paths
        assert "rationale_enum" in diff_paths
        assert "risk_score" in diff_paths
        assert "budget_est" in diff_paths

    def test_unchanged_fields_not_in_diff(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        diff_paths = {op.path for op in diff}
        assert "route_context" not in diff_paths
        assert "candidate_paths" not in diff_paths

    def test_diff_op_values_correct(self, before_state, after_state):
        diff = compute_cognitive_diff(before_state, after_state)
        sp_op = next(op for op in diff if op.path == "selected_path")
        assert sp_op.before == ""
        assert sp_op.after == "standard_validation"

    def test_full_bundle_contains_expected_diff(
        self,
        clock,
        before_state,
        after_state,
    ):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
        )
        d = bundle.to_dict()
        diff_paths = [op["path"] for op in d["diff"]]
        assert diff_paths == sorted(diff_paths)
        assert "selected_path" in diff_paths

    def test_snapshot_unsorted_candidates_raises(self):
        with pytest.raises(ValueError, match="candidate_paths must be sorted"):
            CognitiveStateSnapshot(
                route_context="ctx",
                candidate_paths=("z_path", "a_path"),
                selected_path="z_path",
                rationale_enum="test",
                risk_score=0.0,
                budget_est=0.0,
            )

    def test_diff_op_empty_path_raises(self):
        with pytest.raises(ValueError, match="path must be non-empty"):
            DiffOp(path="", before="a", after="b")

    def test_policy_config_hash_propagated(self, clock, before_state, after_state):
        bundle = emit_cognitive_diff_bundle(
            before=before_state,
            after=after_state,
            semantic_clock=clock,
            policy_config_hash="policy_xyz",
        )
        assert bundle.policy_config_hash == "policy_xyz"
        assert bundle.to_dict()["policy_config_hash"] == "policy_xyz"
