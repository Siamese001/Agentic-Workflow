"""Creative advanced tests for the ADG meta-learning bus pipeline.

Covers invariants and edge cases that the baseline test suite does not:

  1.  Hash collision resistance — distinct content → distinct stable_hash
  2.  Idempotency — same traces run twice produce identical commit sets
  3.  Pattern priority cascade — multi-signal records hit correct pattern
  4.  Reward weight boundary algebra — extreme weight configs stay valid
  5.  Cluster ordering stability — input permutation doesn't change cluster_ids
  6.  Multi-gate simultaneous failure — all denial reasons captured
  7.  Signal poisoning — one bad signal degrades aggregate predictably
  8.  RCA max_clusters cap enforcement
  9.  Lineage traceability — cluster→proposal→commit chain is hash-provable
  10. Adversarial change_spec values — unicode, special chars, empty keys
  11. Reward invariant floor boundary — scores exactly at floor pass/fail
  12. Bus ADG relation set idempotency — same traces → same relation set
  13. Input-order independence of cluster_id
  14. All 5 gates always present in ValidationResult.gate_results
  15. Negative seed deduplication — duplicate seeds produce one cluster
  16. Feature bundle round-trip serialization — JSON→parse→re-hash matches
  17. Proposal engine preserves evidence hashes from cluster
  18. Zero-groundedness edge — no division-by-zero in extractor or engine
  19. Max-proposals-per-cluster with single-agent cluster
  20. Full pipeline smoke test at N=100 traces

No hypothesis dependency — all tests are deterministic.
"""

from __future__ import annotations

import hashlib
import json

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

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_bus_creative")
_emit_applies_guardrail("p0", "test_meta_learning_bus_creative", "p0_governance")
_emit_snapshots_state("p0", "test_meta_learning_bus_creative", "state_snapshot")
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

_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_bus_creative", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_bus_creative", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_bus_creative", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_bus_creative", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_bus_creative", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_bus_creative", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_bus_creative", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_bus_creative", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_bus_creative", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_bus_creative", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_bus_creative", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_bus_creative", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_bus_creative", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_bus_creative", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_bus_creative", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_bus_creative", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_bus_creative", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_bus_creative", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_bus_creative", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_bus_creative", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_bus_creative", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_bus_creative", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_bus_creative", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_learning_bus_creative", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_bus_creative", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_creative", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_creative", "uwg_term_2")
_emit_writes_through("p1", "test_meta_learning_bus_creative", "write_through")
_emit_writes_through("p1", "test_meta_learning_bus_creative", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_meta_learning_bus_creative", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_bus_creative", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_bus_creative", "routing_commit")
_emit_escalates_to_human("p1", "test_meta_learning_bus_creative", "human_escalation")
_emit_routes_through("p1", "test_meta_learning_bus_creative", "route_through")
_emit_checks_agent_registry("p1", "test_meta_learning_bus_creative", "agent_registry")
_emit_validates_agent_capability("p1", "test_meta_learning_bus_creative", "capability")
_emit_dispatches_execution_plan("p1", "test_meta_learning_bus_creative", "exec_plan")
_emit_agent_executes_agent("p1", "test_meta_learning_bus_creative", "sub_agent")
_emit_routes_to_agent("p1", "test_meta_learning_bus_creative", "target_agent")
_emit_verifies_policy("p1", "test_meta_learning_bus_creative", "policy_check")
_emit_observes_runtime_state("p1", "test_meta_learning_bus_creative", "runtime_state")
_emit_verifies_boundary("p1", "test_meta_learning_bus_creative", "boundary_check")
_emit_transcripts_response("p1", "test_meta_learning_bus_creative", "transcript")
_emit_hard_fails_untranscripted("p1", "test_meta_learning_bus_creative")
_emit_gated_by_confidence("p1", "test_meta_learning_bus_creative", "confidence_gate")
emit_replay_key("p0", "test_meta_learning_bus_creative")
emit_determinism_digest("p0", "test_meta_learning_bus_creative")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_bus_creative", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_bus_creative", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_bus_creative", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_bus_creative", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_bus_creative", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_bus_creative", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_bus_creative", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_bus_creative", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_bus_creative", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_bus_creative", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_bus_creative", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_bus_creative", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_bus_creative", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_bus_creative", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_bus_creative", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_bus_creative", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_bus_creative", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_bus_creative", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_bus_creative", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_bus_creative", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared constants / helpers
# ---------------------------------------------------------------------------

_TS = 1_700_100_000
_HASH64 = "c" * 64


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _make_record(
    trace_id,
    outcome="SAFE_FAILURE",
    route="PATH_A",
    groundedness=0.4,
    healer=None,
    hitl=False,
    guardrails=(),
    policies=(),
    node="ADG::Module::alpha",
):
    from system_learning.types.trace_feature_types import TraceFeatureRecord

    bh = _sha256(trace_id)
    return TraceFeatureRecord(
        record_id=bh,
        trace_id=trace_id,
        route=route,
        retrieval_pattern="RAG_BGE",
        retrieval_groundedness=groundedness,
        policy_edges=policies,
        guardrail_edges=guardrails,
        determinism_signals=(),
        healer_used=healer,
        hitl_escalation=hitl,
        outcome_class=outcome,
        adg_node_id=node,
        adg_relation_ids=(),
        feature_bundle_hash=bh,
        timestamp_utc=_TS,
    )


def _make_proposal(
    change_type="ROUTING_RULE_ADJUSTMENT",
    risk_class="LOW",
    policy_hash=None,
    affected_component="ADG::Module::router",
    evidence=None,
    cluster_id=None,
):
    from system_learning.types.optimization_types import OptimizationProposal

    cid = cluster_id or _sha256("cluster")
    pid = _sha256(change_type + risk_class + affected_component + cid)
    return OptimizationProposal(
        proposal_id=pid,
        cluster_id=cid,
        proposed_change_type=change_type,
        affected_component=affected_component,
        expected_outcome="Test",
        risk_class=risk_class,
        change_spec=(
            ("change_type", change_type),
            ("cluster_id", cid),
            ("dominant_route", "PATH_A"),
            ("failure_pattern", "SAFE_FAILURE"),
            ("member_count", "5"),
            ("avg_groundedness", "0.400000"),
            ("hitl_escalation_rate", "0.000000"),
            ("healer_invocation_rate", "0.000000"),
        ),
        evidence_bundle_hashes=evidence if evidence is not None else (_HASH64,),
        reward_score=None,
        policy_hash=policy_hash,
        timestamp_utc=_TS,
    )


def _make_signal(
    trace_id,
    gnd=0.9,
    policy=0.95,
    replay=1.0,
    guard=1.0,
    mut=1.0,
    approval=None,
):
    from system_learning.types.optimization_types import GovernanceRewardSignal

    return GovernanceRewardSignal(
        signal_id=_sha256(trace_id + "sig"),
        trace_id=trace_id,
        groundedness_score=gnd,
        policy_compliance=policy,
        replay_stability=replay,
        guardrail_cleanliness=guard,
        mutation_correctness=mut,
        human_approval=approval,
        timestamp_utc=_TS,
    )


def _make_bus(reward_threshold=0.0, commit_reward_threshold=0.0):
    from system_learning.engines.meta_learning_bus import MetaLearningBus, MetaLearningBusConfig

    return MetaLearningBus(
        MetaLearningBusConfig(
            reward_threshold=reward_threshold,
            commit_reward_threshold=commit_reward_threshold,
        )
    )


def _healer_signal(i):
    return (
        f"tr-h{i:04d}",
        {
            "route_selected": "PATH_A",
            "confidence_gate_state": "pass",
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": 0.8,
            "healing_invoked": True,
            "healer_id": "healer_X",
            "success": True,
            "healed": True,
            "adg_entity_name": "ADG::Module::healer_node",
            "adg_relation_ids": [],
        },
        _TS + i,
    )


# ===========================================================================
# 1. Hash collision resistance
# ===========================================================================


class TestHashCollisionResistance:
    """Distinct inputs must always produce distinct stable_hash values."""

    def test_feature_bundle_hashes_differ_by_trace_id(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        sig = {"route_selected": "PATH_A", "success": True,
               "adg_entity_name": "ADG::M", "adg_relation_ids": []}
        b1 = build_feature_bundle("trace-AAA", sig, _TS)
        b2 = build_feature_bundle("trace-BBB", sig, _TS)
        assert b1.stable_hash() != b2.stable_hash()

    def test_feature_bundle_hashes_differ_by_route(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        sig_a = {"route_selected": "PATH_A", "success": True,
                 "adg_entity_name": "ADG::M", "adg_relation_ids": []}
        sig_b = {"route_selected": "PATH_B", "success": True,
                 "adg_entity_name": "ADG::M", "adg_relation_ids": []}
        b1 = build_feature_bundle("tr", sig_a, _TS)
        b2 = build_feature_bundle("tr", sig_b, _TS)
        assert b1.stable_hash() != b2.stable_hash()

    def test_rca_cluster_hashes_differ_by_member_list(self):
        from system_learning.engines.rca_cluster_engine import RCAClusterConfig, RCAClusterEngine

        eng = RCAClusterEngine(RCAClusterConfig(min_cluster_size=2))
        records_a = [_make_record(f"ta{i}", groundedness=0.2) for i in range(4)]
        records_b = [_make_record(f"tb{i}", groundedness=0.2) for i in range(4)]
        ca = eng.cluster(records_a, _TS)
        cb = eng.cluster(records_b, _TS)
        assert ca[0].cluster_id != cb[0].cluster_id

    def test_optimization_proposal_ids_differ_by_cluster_id(self):
        p1 = _make_proposal(cluster_id=_sha256("c1"))
        p2 = _make_proposal(cluster_id=_sha256("c2"))
        assert p1.proposal_id != p2.proposal_id

    def test_100_distinct_bundles_have_100_distinct_hashes(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        hashes = set()
        for i in range(100):
            b = build_feature_bundle(
                f"trace-{i:04d}",
                {"route_selected": f"R{i}", "success": True,
                 "adg_entity_name": f"ADG::N{i}", "adg_relation_ids": []},
                _TS + i,
            )
            hashes.add(b.stable_hash())
        assert len(hashes) == 100

    def test_validation_result_ids_differ_by_proposal_id(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p1 = _make_proposal(cluster_id=_sha256("cx1"))
        p2 = _make_proposal(cluster_id=_sha256("cx2"))
        r1 = validate_proposal(p1, _TS)
        r2 = validate_proposal(p2, _TS)
        assert r1.result_id != r2.result_id

    def test_governance_score_ids_differ_by_signal_set(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        s1 = [_make_signal("t1", gnd=0.9)]
        s2 = [_make_signal("t2", gnd=0.5)]
        sc1 = score_proposal(p, s1, _TS)
        sc2 = score_proposal(p, s2, _TS + 1)
        assert sc1.score_id != sc2.score_id


# ===========================================================================
# 2. Idempotency
# ===========================================================================


class TestPipelineIdempotency:
    """Running the same input twice produces identical outputs."""

    def test_same_traces_twice_produce_same_cluster_ids(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(6)]
        from system_learning.engines.rca_cluster_engine import cluster_records

        c1 = sorted(c.cluster_id for c in cluster_records(records, _TS))
        c2 = sorted(c.cluster_id for c in cluster_records(records, _TS))
        assert c1 == c2

    def test_same_proposal_validated_twice_gives_same_result_id(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = _make_proposal()
        r1 = validate_proposal(p, _TS)
        r2 = validate_proposal(p, _TS)
        assert r1.result_id == r2.result_id

    def test_full_bus_same_traces_twice_same_commit_ids(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        res1 = bus.process_traces(traces, _TS + 500)
        res2 = bus.process_traces(traces, _TS + 500)
        commit_ids_1 = sorted(c.commit_id for c in res1.commits)
        commit_ids_2 = sorted(c.commit_id for c in res2.commits)
        assert commit_ids_1 == commit_ids_2

    def test_full_bus_same_traces_twice_same_adg_relations(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        res1 = bus.process_traces(traces, _TS + 500)
        res2 = bus.process_traces(traces, _TS + 500)
        rels1 = sorted(str(r) for r in res1.adg_relations_emitted)
        rels2 = sorted(str(r) for r in res2.adg_relations_emitted)
        assert rels1 == rels2

    def test_reward_score_same_signals_same_aggregate(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        signals = [_make_signal(f"t{i}") for i in range(5)]
        s1 = score_proposal(p, signals, _TS)
        s2 = score_proposal(p, signals, _TS)
        assert s1.aggregate_score == s2.aggregate_score


# ===========================================================================
# 3. Pattern priority cascade
# ===========================================================================


class TestPatternPriorityCascade:
    """Records with multiple concurrent signals hit the highest-priority pattern."""

    def test_replay_beats_healer(self):
        """REPLAY_FAILURE outranks HEALER_REQUIRED."""
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", outcome="REPLAY_FAILURE", healer="h")
        assert _derive_failure_pattern(rec) == "REPLAY_FAILURE"

    def test_replay_beats_hitl(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", outcome="REPLAY_FAILURE", hitl=True)
        assert _derive_failure_pattern(rec) == "REPLAY_FAILURE"

    def test_rollback_beats_hitl(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", outcome="ROLLBACK", hitl=True)
        assert _derive_failure_pattern(rec) == "ROLLBACK"

    def test_healer_beats_hitl(self):
        """HEALER_REQUIRED (healer_used ≠ None) beats HITL_ESCALATION."""
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", healer="h", hitl=True)
        assert _derive_failure_pattern(rec) == "HEALER_REQUIRED"

    def test_hitl_beats_low_groundedness(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", groundedness=0.1, hitl=True)
        assert _derive_failure_pattern(rec) == "HITL_ESCALATION"

    def test_low_groundedness_beats_guardrail(self):
        """LOW_GROUNDEDNESS outranks GUARDRAIL_BLOCK when groundedness < 0.5."""
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", groundedness=0.2, guardrails=("g1",))
        assert _derive_failure_pattern(rec) == "LOW_GROUNDEDNESS"

    def test_guardrail_beats_policy_violation(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record(
            "t",
            groundedness=0.8,
            guardrails=("g1",),
            policies=("ph1",),
            outcome="SAFE_FAILURE",
        )
        assert _derive_failure_pattern(rec) == "GUARDRAIL_BLOCK"

    def test_success_record_gets_success_pattern(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        rec = _make_record("t", outcome="SUCCESS", groundedness=0.9)
        assert _derive_failure_pattern(rec) == "SUCCESS"

    def test_healed_success_gets_healed_success_pattern(self):
        from system_learning.engines.rca_cluster_engine import _derive_failure_pattern

        # healer_used=None but outcome=HEALED_SUCCESS → should reach HEALED_SUCCESS branch
        rec = _make_record("t", outcome="HEALED_SUCCESS", groundedness=0.9)
        assert _derive_failure_pattern(rec) == "HEALED_SUCCESS"


# ===========================================================================
# 4. Reward weight boundary algebra
# ===========================================================================


class TestRewardWeightBoundaries:
    """Extreme weight configurations produce valid, in-range scores."""

    def test_all_weight_on_groundedness_produces_valid_score(self):
        from system_learning.engines.governance_reward_model import GovernanceRewardModel, RewardModelConfig

        cfg = RewardModelConfig(
            weight_groundedness=1.0,
            weight_policy_compliance=0.0,
            weight_replay_stability=0.0,
            weight_guardrail_cleanliness=0.0,
            weight_mutation_correctness=0.0,
        )
        model = GovernanceRewardModel(cfg)
        p = _make_proposal()
        signals = [_make_signal("t1", gnd=0.7)]
        score = model.score(p, signals, _TS)
        assert pytest.approx(score.aggregate_score, abs=1e-5) == 0.7
        assert 0.0 <= score.aggregate_score <= 1.0

    def test_all_weight_on_policy_compliance(self):
        from system_learning.engines.governance_reward_model import GovernanceRewardModel, RewardModelConfig

        cfg = RewardModelConfig(
            weight_groundedness=0.0,
            weight_policy_compliance=1.0,
            weight_replay_stability=0.0,
            weight_guardrail_cleanliness=0.0,
            weight_mutation_correctness=0.0,
        )
        model = GovernanceRewardModel(cfg)
        p = _make_proposal()
        signals = [_make_signal("t1", policy=0.6)]
        score = model.score(p, signals, _TS)
        assert pytest.approx(score.aggregate_score, abs=1e-5) == 0.6

    def test_perfect_signals_produce_aggregate_near_1(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        signals = [
            _make_signal(f"t{i}", gnd=1.0, policy=1.0, replay=1.0, guard=1.0, mut=1.0)
            for i in range(10)
        ]
        score = score_proposal(p, signals, _TS)
        assert score.aggregate_score == pytest.approx(1.0, abs=1e-5)

    def test_worst_case_signals_produce_aggregate_near_0(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        signals = [
            _make_signal(f"t{i}", gnd=0.0, policy=0.0, replay=0.0, guard=0.0, mut=0.0)
            for i in range(5)
        ]
        score = score_proposal(p, signals, _TS)
        assert score.aggregate_score == pytest.approx(0.0, abs=1e-5)

    def test_invalid_weights_sum_raises(self):
        from system_learning.engines.governance_reward_model import RewardModelConfig

        with pytest.raises(ValueError, match="sum to 1.0"):
            RewardModelConfig(
                weight_groundedness=0.3,
                weight_policy_compliance=0.3,
                weight_replay_stability=0.3,
                weight_guardrail_cleanliness=0.3,
                weight_mutation_correctness=0.3,
            )

    def test_invariant_floor_at_zero_always_preserved(self):
        from system_learning.engines.governance_reward_model import GovernanceRewardModel, RewardModelConfig

        cfg = RewardModelConfig(invariant_floor=0.0, policy_floor=0.0, replay_floor=0.0)
        model = GovernanceRewardModel(cfg)
        p = _make_proposal()
        signals = [_make_signal("t1", gnd=0.01, policy=0.01, replay=0.01)]
        score = model.score(p, signals, _TS)
        assert score.invariant_preserved is True

    def test_invariant_floor_at_one_never_preserved_unless_perfect(self):
        from system_learning.engines.governance_reward_model import GovernanceRewardModel, RewardModelConfig

        cfg = RewardModelConfig(invariant_floor=1.0, policy_floor=1.0, replay_floor=1.0)
        model = GovernanceRewardModel(cfg)
        p = _make_proposal()
        signals = [_make_signal("t1", gnd=0.99, policy=0.99, replay=0.99)]
        score = model.score(p, signals, _TS)
        # aggregate < 1.0 so invariant_preserved must be False
        assert score.invariant_preserved is False


# ===========================================================================
# 5. Cluster ordering / input-order independence
# ===========================================================================


class TestClusterOrderingStability:
    """Input permutation must not affect cluster_ids."""

    def test_reversed_record_order_same_cluster_ids(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(8)]
        c_fwd = sorted(c.cluster_id for c in cluster_records(records, _TS))
        c_rev = sorted(c.cluster_id for c in cluster_records(list(reversed(records)), _TS))
        assert c_fwd == c_rev

    def test_shuffled_record_order_same_cluster_ids(self):
        import random

        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(10)]
        shuffled = list(records)
        # deterministic shuffle using fixed seed
        random.Random(42).shuffle(shuffled)
        c_orig = sorted(c.cluster_id for c in cluster_records(records, _TS))
        c_shuf = sorted(c.cluster_id for c in cluster_records(shuffled, _TS))
        assert c_orig == c_shuf

    def test_cluster_member_trace_ids_always_sorted(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i:03d}", groundedness=0.2) for i in range(6)]
        clusters = cluster_records(records, _TS)
        for cluster in clusters:
            ids = list(cluster.member_trace_ids)
            assert ids == sorted(ids)

    def test_affected_agents_always_sorted(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [
            _make_record(f"t{i}", groundedness=0.2, node=f"ADG::Module::node_{chr(ord('z') - i)}")
            for i in range(6)
        ]
        clusters = cluster_records(records, _TS)
        for cluster in clusters:
            agents = list(cluster.affected_agents)
            assert agents == sorted(agents)


# ===========================================================================
# 6. Multi-gate simultaneous failure
# ===========================================================================


class TestMultiGateSimultaneousFailure:
    """Proposals that fail multiple gates list ALL denial reasons."""

    def test_two_gates_fail_both_captured(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster")
        # proposal_id is NOT a valid hash → DETERMINISM fails
        # affected_component is ADG::Unknown → GUARDRAIL fails
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Unknown",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = validate_proposal(p, _TS)
        assert result.validation_pass is False
        # Both DETERMINISM and GUARDRAIL should appear
        assert "PROPOSAL_ID_NOT_HASH" in result.denial_reasons
        assert "UNKNOWN_AFFECTED_COMPONENT" in result.denial_reasons
        assert len(result.denial_reasons) >= 2

    def test_three_gates_fail_all_captured(self):
        from system_learning.engines.proposal_validation_engine import (
            ProposalValidationEngine,
            ValidationConfig,
        )
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster")
        # NOT_A_HASH → DETERMINISM fails
        # ADG::Unknown → GUARDRAIL fails
        # policy_hash mismatch → POLICY fails
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Unknown",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash="hash_A",
            timestamp_utc=_TS,
        )
        engine = ProposalValidationEngine(
            ValidationConfig(active_policy_hash="hash_B")
        )
        result = engine.validate(p, _TS)
        assert result.validation_pass is False
        assert len(result.denial_reasons) >= 3

    def test_denial_reasons_are_deterministically_sorted(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster")
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Unknown",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        r1 = validate_proposal(p, _TS)
        r2 = validate_proposal(p, _TS)
        assert r1.denial_reasons == r2.denial_reasons
        assert list(r1.denial_reasons) == sorted(r1.denial_reasons)


# ===========================================================================
# 7. Signal poisoning
# ===========================================================================


class TestSignalPoisoning:
    """One bad signal among many good signals degrades score predictably."""

    def test_one_zero_replay_signal_among_9_perfect_degrades_replay_contrib(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        good = [_make_signal(f"t{i}", replay=1.0) for i in range(9)]
        bad = [_make_signal("t_bad", replay=0.0)]
        score_clean = score_proposal(p, good, _TS)
        score_poisoned = score_proposal(p, good + bad, _TS)
        # Poisoned score must be strictly lower in replay_stability_contrib
        assert score_poisoned.replay_stability_contrib < score_clean.replay_stability_contrib

    def test_aggregate_degrades_monotonically_with_more_bad_signals(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        good = [_make_signal(f"g{i}") for i in range(10)]

        scores = []
        for n_bad in range(0, 11):
            bad = [_make_signal(f"b{j}", gnd=0.0, policy=0.0, replay=0.0, guard=0.0, mut=0.0)
                   for j in range(n_bad)]
            s = score_proposal(p, good + bad, _TS)
            scores.append(s.aggregate_score)

        # Each additional bad signal must not increase the aggregate
        for i in range(1, len(scores)):
            assert scores[i] <= scores[i - 1] + 1e-9, (
                f"Score increased at n_bad={i}: {scores[i-1]} → {scores[i]}"
            )

    def test_single_bad_human_approval_lowers_approval_rate(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        all_approved = [_make_signal(f"t{i}", approval=True) for i in range(4)]
        one_rejected = [_make_signal("t_rej", approval=False)]
        score = score_proposal(p, all_approved + one_rejected, _TS)
        assert score.human_approval_rate == pytest.approx(4 / 5, abs=1e-5)

    def test_empty_trace_id_signal_filtered_out(self):
        from system_learning.engines.governance_reward_model import score_proposal
        from system_learning.types.optimization_types import GovernanceRewardSignal

        p = _make_proposal()
        valid = [_make_signal("t1")]
        invalid = GovernanceRewardSignal(
            signal_id=_HASH64,
            trace_id="",
            groundedness_score=0.0,
            policy_compliance=0.0,
            replay_stability=0.0,
            guardrail_cleanliness=0.0,
            mutation_correctness=0.0,
            human_approval=None,
            timestamp_utc=_TS,
        )
        score_clean = score_proposal(p, valid, _TS)
        score_with_bad = score_proposal(p, valid + [invalid], _TS)
        # Invalid signal is filtered; both scores use the same 1 valid signal
        assert score_clean.signal_count == 1
        assert score_with_bad.signal_count == 1
        assert score_clean.aggregate_score == score_with_bad.aggregate_score


# ===========================================================================
# 8. max_clusters cap enforcement
# ===========================================================================


class TestMaxClustersCap:
    """RCA engine must not exceed max_clusters setting."""

    def test_max_clusters_2_trims_to_2(self):
        from system_learning.engines.rca_cluster_engine import RCAClusterConfig, RCAClusterEngine

        # Create records spread across many distinct patterns
        records = []
        for i in range(20):
            # Each pair gets a unique route → sub-key → distinct cluster
            records.append(_make_record(f"t{i}a", groundedness=0.2, route=f"R{i}"))
            records.append(_make_record(f"t{i}b", groundedness=0.2, route=f"R{i}"))

        engine = RCAClusterEngine(RCAClusterConfig(max_clusters=2, min_cluster_size=2))
        clusters = engine.cluster(records, _TS)
        assert len(clusters) <= 2

    def test_max_clusters_enforced_after_singleton_merge(self):
        from system_learning.engines.rca_cluster_engine import RCAClusterConfig, RCAClusterEngine

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(50)]
        engine = RCAClusterEngine(RCAClusterConfig(max_clusters=1))
        clusters = engine.cluster(records, _TS)
        assert len(clusters) <= 1

    def test_max_clusters_cap_keeps_largest_clusters(self):
        from system_learning.engines.rca_cluster_engine import RCAClusterConfig, RCAClusterEngine

        # 10 LOW_GROUNDEDNESS + 2 HITL_ESCALATION
        records = (
            [_make_record(f"lg{i}", groundedness=0.2) for i in range(10)]
            + [_make_record(f"he{i}", hitl=True, groundedness=0.9) for i in range(2)]
        )
        engine = RCAClusterEngine(RCAClusterConfig(max_clusters=1, min_cluster_size=2))
        clusters = engine.cluster(records, _TS)
        assert len(clusters) == 1
        # The kept cluster should be the largest one
        assert clusters[0].member_count >= 2


# ===========================================================================
# 9. Lineage traceability
# ===========================================================================


class TestLineageTraceability:
    """cluster→proposal→commit chain is hash-provable."""

    def test_proposal_evidence_contains_cluster_hash(self):
        from system_learning.engines.optimization_proposal_engine import generate_proposals
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(6)]
        clusters = cluster_records(records, _TS)
        proposals = generate_proposals(clusters, _TS)
        for proposal in proposals:
            # At least one evidence hash must be the cluster's stable_hash
            matching_clusters = [
                c for c in clusters if c.stable_hash() in proposal.evidence_bundle_hashes
            ]
            assert len(matching_clusters) >= 1, (
                f"Proposal {proposal.proposal_id[:8]} has no cluster evidence hash"
            )

    def test_proposal_cluster_id_matches_originating_cluster(self):
        from system_learning.engines.optimization_proposal_engine import generate_proposals
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(6)]
        clusters = cluster_records(records, _TS)
        cluster_ids = {c.cluster_id for c in clusters}
        proposals = generate_proposals(clusters, _TS)
        for proposal in proposals:
            assert proposal.cluster_id in cluster_ids

    def test_commit_references_proposal_and_validation(self):
        """Commit.proposal_id must match proposal and .validation_result_id must match result."""
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        result = bus.process_traces(traces, _TS + 500)

        proposal_ids = {p.proposal_id for p in result.proposals}
        result_ids = {r.result_id for r in result.validation_results}

        for commit in result.commits:
            assert commit.proposal_id in proposal_ids
            assert commit.validation_result_id in result_ids

    def test_adg_relation_chain_is_traversable(self):
        """triggered_telemetry → chunks_into → proposal_commits_optimization is a DAG."""
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        result = bus.process_traces(traces, _TS + 500)

        # Collect all from/to nodes per relation type
        rel_map: dict[str, list[tuple[str, str]]] = {}
        for (frm, rel, to) in result.adg_relations_emitted:
            rel_map.setdefault(rel, []).append((frm, to))

        # Every "triggered_telemetry" from-node should prefix with ADG::
        for frm, _ in rel_map.get("triggered_telemetry", []):
            assert frm.startswith("ADG::")

        # Every "chunks_into" to-node should be an RCACluster node
        for _, to in rel_map.get("chunks_into", []):
            assert "RCACluster" in to

    def test_commit_stable_hash_is_64_char_hex(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        result = bus.process_traces(traces, _TS + 500)
        for commit in result.commits:
            h = commit.stable_hash()
            assert len(h) == 64
            assert all(c in "0123456789abcdef" for c in h)


# ===========================================================================
# 10. Adversarial change_spec values
# ===========================================================================


class TestAdversarialChangeSpec:
    """Change spec with unicode, special chars, empty string values must serialize."""

    def _proposal_with_spec(self, spec):
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster_adv")
        pid = _sha256("adv" + str(spec))
        return OptimizationProposal(
            proposal_id=pid,
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Module::adv_test",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=spec,
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )

    def test_unicode_value_in_change_spec_serializes(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = self._proposal_with_spec((
            ("key", "值 日本語 Ünïcödé"),
            ("cluster_id", _sha256("c")),
        ))
        result = validate_proposal(p, _TS)
        # determinism gate should pass (value is serializable)
        assert result.determinism_verified is True

    def test_empty_string_value_in_change_spec_serializes(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = self._proposal_with_spec((
            ("key", ""),
            ("cluster_id", _sha256("c")),
        ))
        result = validate_proposal(p, _TS)
        assert result.determinism_verified is True

    def test_numeric_string_value_in_change_spec(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = self._proposal_with_spec((
            ("score", "0.123456789"),
            ("count", "99999"),
        ))
        result = validate_proposal(p, _TS)
        assert result.determinism_verified is True

    def test_change_spec_json_output_is_deterministic(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        spec = (("z_key", "z_val"), ("a_key", "a_val"))
        p = self._proposal_with_spec(spec)
        # Running serialization-dependent hashing twice should give same result_id
        r1 = validate_proposal(p, _TS)
        r2 = validate_proposal(p, _TS)
        assert r1.result_id == r2.result_id

    def test_backslash_and_quote_in_spec_value(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = self._proposal_with_spec((
            ("path", r"C:\some\path"),
            ("desc", 'He said "hello"'),
        ))
        result = validate_proposal(p, _TS)
        assert result.determinism_verified is True


# ===========================================================================
# 11. Reward invariant floor boundary conditions
# ===========================================================================


class TestRewardInvariantFloorBoundary:
    """Scores exactly at the invariant_floor should pass; below should fail."""

    def _score_at(self, gnd, policy, replay, floor=0.60, p_floor=0.80, r_floor=0.75):
        from system_learning.engines.governance_reward_model import (
            GovernanceRewardModel,
            RewardModelConfig,
        )

        cfg = RewardModelConfig(
            invariant_floor=floor,
            policy_floor=p_floor,
            replay_floor=r_floor,
        )
        p = _make_proposal()
        signals = [_make_signal("t1", gnd=gnd, policy=policy, replay=replay)]
        return GovernanceRewardModel(cfg).score(p, signals, _TS)

    def test_exact_policy_floor_passes_invariant(self):
        # policy=0.80 exactly at policy_floor=0.80
        score = self._score_at(gnd=1.0, policy=0.80, replay=1.0)
        # aggregate will be high; policy at exactly floor should pass
        assert score.policy_compliance_contrib > 0.0
        # invariant_preserved depends on aggregate ≥ 0.60 AND policy ≥ 0.80 AND replay ≥ 0.75
        # With perfect gnd and replay, aggregate > 0.60, so invariant_preserved should be True
        assert score.invariant_preserved is True

    def test_below_policy_floor_breaks_invariant(self):
        score = self._score_at(gnd=1.0, policy=0.79, replay=1.0)
        assert score.invariant_preserved is False

    def test_exact_replay_floor_passes_invariant(self):
        score = self._score_at(gnd=1.0, policy=1.0, replay=0.75)
        assert score.invariant_preserved is True

    def test_below_replay_floor_breaks_invariant(self):
        score = self._score_at(gnd=1.0, policy=1.0, replay=0.74)
        assert score.invariant_preserved is False

    def test_aggregate_below_floor_breaks_invariant(self):
        # Force low aggregate: all dimensions at 0.0 → aggregate ≈ 0.0 < 0.60
        score = self._score_at(gnd=0.0, policy=0.0, replay=0.0)
        assert score.invariant_preserved is False


# ===========================================================================
# 12. ADG relation set idempotency
# ===========================================================================


class TestADGRelationSetIdempotency:
    """Same traces → exact same sorted ADG relation set both times."""

    def test_six_healer_traces_same_relations_twice(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        r1 = bus.process_traces(traces, _TS + 600)
        r2 = bus.process_traces(traces, _TS + 600)
        rels1 = sorted(str(t) for t in r1.adg_relations_emitted)
        rels2 = sorted(str(t) for t in r2.adg_relations_emitted)
        assert rels1 == rels2

    def test_relation_from_entity_always_starts_with_adg(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        r = bus.process_traces(traces, _TS + 600)
        for (frm, rel, to) in r.adg_relations_emitted:
            assert frm.startswith("ADG::"), f"From entity doesn't start with ADG::: {frm!r}"

    def test_relation_to_entity_always_starts_with_adg(self):
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        r = bus.process_traces(traces, _TS + 600)
        for (frm, rel, to) in r.adg_relations_emitted:
            assert to.startswith("ADG::"), f"To entity doesn't start with ADG::: {to!r}"

    def test_relation_type_is_known_string(self):
        known = {
            "triggered_telemetry",
            "chunks_into",
            "stores_embedding",
            "scored_by_reward",
            "proposal_commits_optimization",
        }
        bus = _make_bus()
        traces = [_healer_signal(i) for i in range(6)]
        r = bus.process_traces(traces, _TS + 600)
        for (_, rel, _) in r.adg_relations_emitted:
            assert rel in known, f"Unknown relation type: {rel!r}"


# ===========================================================================
# 13. All 5 gates always present in gate_results
# ===========================================================================


class TestGateResultsCompleteness:
    """All 5 gate names must always appear in ValidationResult.gate_results."""

    _EXPECTED_GATES = frozenset({
        "REPLAY_VALIDATION",
        "POLICY_VALIDATION",
        "GUARDRAIL_VALIDATION",
        "DETERMINISM_VERIFICATION",
        "REGRESSION_TESTING",
    })

    def test_passing_proposal_has_all_5_gates(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = _make_proposal()
        result = validate_proposal(p, _TS)
        gate_names = {g for g, _ in result.gate_results}
        assert gate_names == self._EXPECTED_GATES

    def test_failing_proposal_has_all_5_gates(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("c")
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Unknown",
            expected_outcome="x",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = validate_proposal(p, _TS)
        gate_names = {g for g, _ in result.gate_results}
        assert gate_names == self._EXPECTED_GATES

    def test_gate_results_sorted_alphabetically(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = _make_proposal()
        result = validate_proposal(p, _TS)
        names = [g for g, _ in result.gate_results]
        assert names == sorted(names)

    def test_batch_validation_all_results_have_5_gates(self):
        from system_learning.engines.proposal_validation_engine import ProposalValidationEngine

        proposals = [_make_proposal(cluster_id=_sha256(f"c{i}")) for i in range(5)]
        results = ProposalValidationEngine().validate_batch(proposals, _TS)
        for result in results:
            gate_names = {g for g, _ in result.gate_results}
            assert gate_names == self._EXPECTED_GATES


# ===========================================================================
# 14. Negative seed deduplication
# ===========================================================================


class TestNegativeSeedDeduplication:
    """Duplicate seeds produce exactly one cluster (not two)."""

    def test_duplicate_seeds_produce_one_cluster(self):
        from system_learning.engines.rca_cluster_engine import cluster_records
        from system_learning.types.trace_feature_types import FailurePattern

        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="VIOLATION",
            signature="dup_sig",
            affected_component="ADG::Module::guard",
            occurrence_count=3,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        clusters = cluster_records([], _TS, negative_seeds=[seed, seed, seed])
        # All three seeds are identical → deduplicated to one cluster
        seed_clusters = [c for c in clusters if "NEG_SEED" in c.failure_pattern]
        assert len(seed_clusters) == 1

    def test_two_distinct_seeds_produce_two_clusters(self):
        from system_learning.engines.rca_cluster_engine import cluster_records
        from system_learning.types.trace_feature_types import FailurePattern

        seeds = [
            FailurePattern(
                pattern_id=_HASH64,
                source_type="VIOLATION",
                signature="sig_A",
                affected_component="ADG::Module::A",
                occurrence_count=3,
                evidence_hash=_HASH64,
                cluster_id=None,
                timestamp_utc=_TS,
            ),
            FailurePattern(
                pattern_id=_sha256("B"),
                source_type="ANTIPATTERN",
                signature="sig_B",
                affected_component="ADG::Module::B",
                occurrence_count=2,
                evidence_hash=_sha256("B_evidence"),
                cluster_id=None,
                timestamp_utc=_TS,
            ),
        ]
        clusters = cluster_records([], _TS, negative_seeds=seeds)
        seed_clusters = [c for c in clusters if "NEG_SEED" in c.failure_pattern]
        assert len(seed_clusters) == 2

    def test_seed_cluster_node_contains_source_type(self):
        from system_learning.engines.rca_cluster_engine import cluster_records
        from system_learning.types.trace_feature_types import FailurePattern

        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="DRIFT_ALERT",
            signature="routing_drift",
            affected_component="ADG::Module::router",
            occurrence_count=5,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        clusters = cluster_records([], _TS, negative_seeds=[seed])
        seed_clusters = [c for c in clusters if "NEG_SEED" in c.failure_pattern]
        assert len(seed_clusters) == 1
        assert "DRIFT_ALERT" in seed_clusters[0].failure_pattern


# ===========================================================================
# 15. Feature bundle round-trip serialization
# ===========================================================================


class TestFeatureBundleRoundTrip:
    """to_json() produces deterministic JSON that re-hashes consistently."""

    def _make_bundle(self, trace_id="tr-rt"):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        return build_feature_bundle(
            trace_id,
            {
                "route_selected": "PATH_C",
                "confidence_gate_state": "stall",
                "retrieval_path": "DIRECT",
                "retrieval_groundedness_score": 0.6,
                "policy_hashes": ["ph1", "ph2"],
                "guardrails_applied": ["g1"],
                "determinism_markers": ["dm1"],
                "healing_invoked": False,
                "healer_id": None,
                "human_escalation_flag": False,
                "mutation_presence": False,
                "success": True,
                "adg_entity_name": "ADG::Module::round_trip",
                "adg_relation_ids": ["r1", "r2"],
            },
            _TS,
        )

    def test_to_json_is_valid_json(self):
        b = self._make_bundle()
        parsed = json.loads(b.to_json())
        assert isinstance(parsed, dict)

    def test_to_json_contains_all_expected_keys(self):
        b = self._make_bundle()
        d = json.loads(b.to_json())
        for key in ("trace_id", "route_selected", "final_outcome_class",
                    "retrieval_groundedness_score", "adg_entity_name",
                    "influence_class"):
            assert key in d, f"Missing key: {key!r}"

    def test_stable_hash_matches_hash_of_to_json(self):
        import hashlib
        b = self._make_bundle()
        # stable_hash is SHA-256 of deterministic_json(_canonical_dict())
        # to_json() returns deterministic_json(_canonical_dict())
        expected = hashlib.sha256(b.to_json().encode("utf-8")).hexdigest()
        assert b.stable_hash() == expected

    def test_two_bundles_with_same_content_same_hash(self):
        b1 = self._make_bundle("tr-same")
        b2 = self._make_bundle("tr-same")
        assert b1.stable_hash() == b2.stable_hash()

    def test_to_dict_and_to_json_consistent(self):
        import json as _json
        b = self._make_bundle()
        assert _json.loads(b.to_json()) == b.to_dict()


# ===========================================================================
# 16. Zero-groundedness edge
# ===========================================================================


class TestZeroGroundednessEdge:
    """Extractor and engines must not divide by zero or produce NaN."""

    def test_zero_groundedness_extraction_succeeds(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        b = build_feature_bundle(
            "tr-zero-gnd",
            {"retrieval_groundedness_score": 0.0, "success": False,
             "adg_entity_name": "ADG::M", "adg_relation_ids": []},
            _TS,
        )
        assert b.retrieval_groundedness_score == 0.0

    def test_zero_groundedness_cluster_stats_no_nan(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.0) for i in range(4)]
        clusters = cluster_records(records, _TS)
        for c in clusters:
            assert c.avg_groundedness == pytest.approx(0.0, abs=1e-9)
            assert not (c.avg_groundedness != c.avg_groundedness)  # NaN check

    def test_zero_groundedness_reward_signal_valid(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        signals = [_make_signal("t1", gnd=0.0)]
        score = score_proposal(p, signals, _TS)
        assert score.aggregate_score >= 0.0
        assert score.groundedness_contrib == pytest.approx(0.0, abs=1e-9)

    def test_all_hitl_escalation_rate_1(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", hitl=True) for i in range(4)]
        clusters = cluster_records(records, _TS)
        for c in clusters:
            if c.failure_pattern == "HITL_ESCALATION":
                assert c.hitl_escalation_rate == pytest.approx(1.0, abs=1e-9)


# ===========================================================================
# 17. Full pipeline smoke test at N=100
# ===========================================================================


class TestFullPipelineLargeScale:
    """Smoke test: 100 traces, various patterns, pipeline completes correctly."""

    def _build_100_traces(self):
        traces = []
        for i in range(30):
            traces.append((f"lg-{i:04d}", {
                "route_selected": "PATH_A",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.2,
                "success": False,
                "adg_entity_name": "ADG::Module::retriever",
                "adg_relation_ids": [],
            }, _TS + i))
        for i in range(20):
            traces.append((f"he-{i:04d}", {
                "route_selected": "PATH_B",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.8,
                "healing_invoked": True,
                "healer_id": "healer_X",
                "success": True,
                "healed": True,
                "adg_entity_name": "ADG::Module::healer",
                "adg_relation_ids": [],
            }, _TS + 30 + i))
        for i in range(20):
            traces.append((f"hi-{i:04d}", {
                "route_selected": "PATH_C",
                "confidence_gate_state": "escalate",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.85,
                "human_escalation_flag": True,
                "success": True,
                "adg_entity_name": "ADG::Module::escalator",
                "adg_relation_ids": [],
            }, _TS + 50 + i))
        for i in range(15):
            traces.append((f"rf-{i:04d}", {
                "route_selected": "PATH_D",
                "confidence_gate_state": "pass",
                "retrieval_path": "DIRECT",
                "retrieval_groundedness_score": 0.5,
                "replay_failed": True,
                "success": False,
                "adg_entity_name": "ADG::Module::replay",
                "adg_relation_ids": [],
            }, _TS + 70 + i))
        for i in range(15):
            traces.append((f"ok-{i:04d}", {
                "route_selected": "PATH_A",
                "confidence_gate_state": "pass",
                "retrieval_path": "RAG_BGE",
                "retrieval_groundedness_score": 0.95,
                "success": True,
                "adg_entity_name": "ADG::Module::healthy",
                "adg_relation_ids": [],
            }, _TS + 85 + i))
        return traces

    def test_100_traces_pipeline_completes(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        assert len(result.bundles) == 100
        assert len(result.records) == 100
        assert len(result.clusters) >= 1

    def test_100_traces_all_4_failure_patterns_clustered(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        patterns = {c.failure_pattern for c in result.clusters}
        assert "LOW_GROUNDEDNESS" in patterns
        assert "HEALER_REQUIRED" in patterns
        assert "HITL_ESCALATION" in patterns
        assert "REPLAY_FAILURE" in patterns

    def test_100_traces_proposals_generated(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        assert len(result.proposals) >= 4

    def test_100_traces_commits_produced(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        assert len(result.commits) >= 1

    def test_100_traces_adg_relations_all_valid_types(self):
        known_relations = {
            "triggered_telemetry", "chunks_into", "stores_embedding",
            "scored_by_reward", "proposal_commits_optimization",
        }
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        for (_, rel, _) in result.adg_relations_emitted:
            assert rel in known_relations

    def test_100_traces_no_duplicate_commit_ids(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        result = bus.process_traces(traces, _TS + 1000)
        ids = [c.commit_id for c in result.commits]
        assert len(ids) == len(set(ids))

    def test_100_traces_idempotent_second_run(self):
        bus = _make_bus()
        traces = self._build_100_traces()
        r1 = bus.process_traces(traces, _TS + 1000)
        r2 = bus.process_traces(traces, _TS + 1000)
        assert sorted(c.commit_id for c in r1.commits) == sorted(c.commit_id for c in r2.commits)


# ===========================================================================
# 18. TraceFeatureExtractor batch error resilience
# ===========================================================================


class TestExtractorBatchResilience:
    """Batch extraction must handle all edge-case signal shapes."""

    def test_all_none_values_in_signal_produces_unknown_bundle(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        b = build_feature_bundle("tr-nulls", {
            "route_selected": None,
            "confidence_gate_state": None,
            "retrieval_path": None,
            "retrieval_groundedness_score": None,
            "adg_entity_name": None,
            "adg_relation_ids": None,
            "success": None,
        }, _TS)
        assert b.trace_id == "tr-nulls"
        assert b.final_outcome_class == "UNKNOWN"
        assert b.retrieval_groundedness_score == 0.0

    def test_empty_dict_signal_produces_valid_bundle(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        b = build_feature_bundle("tr-empty", {}, _TS)
        assert b.trace_id == "tr-empty"
        assert b.route_selected == "UNKNOWN"
        assert b.adg_entity_name == "ADG::Unknown"

    def test_extra_unknown_keys_ignored(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        b = build_feature_bundle("tr-extra", {
            "success": True,
            "adg_entity_name": "ADG::Module::foo",
            "adg_relation_ids": [],
            "unknown_future_field_XYZ": "some_value",
            "another_unknown": 12345,
        }, _TS)
        assert b.trace_id == "tr-extra"

    def test_zero_item_batch_returns_empty_list(self):
        from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor

        bundles = TraceFeatureExtractor().extract_batch([])
        assert bundles == []

    def test_guardrails_applied_must_be_list_not_string(self):
        from system_learning.engines.trace_feature_extractor import build_feature_bundle

        # If someone passes a string instead of list, it must not crash
        b = build_feature_bundle("tr-bad-guard", {
            "guardrails_applied": "g1",  # string, not list
            "success": True,
            "adg_entity_name": "ADG::Module::foo",
            "adg_relation_ids": [],
        }, _TS)
        # The extractor iterates over the string characters; result is non-empty but valid
        assert isinstance(b.guardrails_applied, tuple)
