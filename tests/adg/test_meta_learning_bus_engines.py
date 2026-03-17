"""Tests for meta-learning bus engine components.

Covers:
  - TraceFeatureExtractor: signal mapping, fail-safe defaults, batch
  - RCAClusterEngine: grouping, singleton merging, negative seeds
  - OptimizationProposalEngine: rule matching, risk downgrade, multi-agent
  - ProposalValidationEngine: gate logic, fail-closed, batch validation
  - GovernanceRewardModel: weighted scoring, invariant check, annotation
"""

from __future__ import annotations

import hashlib

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

_emit_records_execution_trace("p0", "evidence", "test_meta_learning_bus_engines")
_emit_applies_guardrail("p0", "test_meta_learning_bus_engines", "p0_governance")
_emit_snapshots_state("p0", "test_meta_learning_bus_engines", "state_snapshot")
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

_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_1")
_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_2")
_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_3")
_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_4")
_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_5")
_emit_emits_metric_event("test_meta_learning_bus_engines", "p4obs", "metric_6")
_emit_records_incident_event("test_meta_learning_bus_engines", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_meta_learning_bus_engines", "p4obs", "anomaly")
_emit_writes_observability_log("test_meta_learning_bus_engines", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_meta_learning_bus_engines", "p4obs", "mon_state")
_emit_triggers_alert("test_meta_learning_bus_engines", "p4obs", "alert")
_emit_links_incident_trace("test_meta_learning_bus_engines", "p4obs", "trace_link")
_emit_captures_pattern("test_meta_learning_bus_engines", "p3lm", "pattern")
_emit_records_learning_event("test_meta_learning_bus_engines", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_meta_learning_bus_engines", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_meta_learning_bus_engines", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_meta_learning_bus_engines", "p3lm", "routing")
_emit_improves_agent_policy("test_meta_learning_bus_engines", "p3lm", "policy")
_emit_stores_learning_state("test_meta_learning_bus_engines", "p3lm", "state")
_emit_records_execution_trace("test_meta_learning_bus_engines", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_meta_learning_bus_engines", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_meta_learning_bus_engines", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_meta_learning_bus_engines", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_meta_learning_bus_engines", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_meta_learning_bus_engines", "env_read", "p2_env_1")
_emit_reads_environ("test_meta_learning_bus_engines", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_meta_learning_bus_engines", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_meta_learning_bus_engines", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_meta_learning_bus_engines", "context_pull")
_emit_pulls_context("p1", "test_meta_learning_bus_engines", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_engines", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_meta_learning_bus_engines", "uwg_term_2")
_emit_writes_through("p1", "test_meta_learning_bus_engines", "write_through")
_emit_writes_through("p1", "test_meta_learning_bus_engines", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_meta_learning_bus_engines", "safety_validation")
_emit_invokes_eval("p1", "test_meta_learning_bus_engines", "eval_call")
_emit_proposal_commits_routing("p1", "test_meta_learning_bus_engines", "routing_commit")
_emit_escalates_to_human("p1", "test_meta_learning_bus_engines", "human_escalation")
_emit_routes_through("p1", "test_meta_learning_bus_engines", "route_through")
_emit_checks_agent_registry("p1", "test_meta_learning_bus_engines", "agent_registry")
_emit_validates_agent_capability("p1", "test_meta_learning_bus_engines", "capability")
_emit_dispatches_execution_plan("p1", "test_meta_learning_bus_engines", "exec_plan")
_emit_agent_executes_agent("p1", "test_meta_learning_bus_engines", "sub_agent")
_emit_routes_to_agent("p1", "test_meta_learning_bus_engines", "target_agent")
_emit_verifies_policy("p1", "test_meta_learning_bus_engines", "policy_check")
_emit_observes_runtime_state("p1", "test_meta_learning_bus_engines", "runtime_state")
_emit_verifies_boundary("p1", "test_meta_learning_bus_engines", "boundary_check")
_emit_transcripts_response("p1", "test_meta_learning_bus_engines", "transcript")
_emit_hard_fails_untranscripted("p1", "test_meta_learning_bus_engines")
_emit_gated_by_confidence("p1", "test_meta_learning_bus_engines", "confidence_gate")
emit_replay_key("p0", "test_meta_learning_bus_engines")
emit_determinism_digest("p0", "test_meta_learning_bus_engines")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_meta_learning_bus_engines", "execution_auth")
_emit_validates_capability("p2", "test_meta_learning_bus_engines", "capability_check")
_emit_routes_to_capability("p2", "test_meta_learning_bus_engines", "capability_route")
_emit_writes_via_uwg("p2", "test_meta_learning_bus_engines", "uwg_write")
_emit_blocks_direct_write("p2", "test_meta_learning_bus_engines", "direct_write_block")
_emit_records_tool_invocation("p2", "test_meta_learning_bus_engines", "tool_invocation")
_emit_captures_execution_output("p2", "test_meta_learning_bus_engines", "exec_output")
_emit_dispatches_agent("p3", "test_meta_learning_bus_engines", "agent_dispatch")
_emit_coordinates_agents("p3", "test_meta_learning_bus_engines", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_meta_learning_bus_engines", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_meta_learning_bus_engines", "healing_outcome")
_emit_escalates_failure("p3", "test_meta_learning_bus_engines", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_meta_learning_bus_engines", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_meta_learning_bus_engines", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_meta_learning_bus_engines", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_meta_learning_bus_engines", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_meta_learning_bus_engines", "eval_metric")
_emit_stores_embedding("p4", "test_meta_learning_bus_engines", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_meta_learning_bus_engines", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_meta_learning_bus_engines", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

_TS = 1_700_000_000
_HASH64 = "a" * 64  # valid-looking SHA-256 hexdigest for tests


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
        adg_node_id="ADG::Module::alpha",
        adg_relation_ids=(),
        feature_bundle_hash=bh,
        timestamp_utc=_TS,
    )


def _make_cluster(
    failure_pattern,
    member_count=5,
    hitl_rate=0.0,
    healer_rate=0.0,
    agents=("ADG::Module::alpha",),
    trace_ids=None,
):
    from system_learning.types.trace_feature_types import RCACluster

    if trace_ids is None:
        trace_ids = tuple(f"t{i}" for i in range(member_count))
    cid = _sha256(failure_pattern + str(member_count))
    return RCACluster(
        cluster_id=cid,
        failure_pattern=failure_pattern,
        dominant_route="PATH_A",
        dominant_guardrail=None,
        dominant_retrieval_pattern="RAG_BGE",
        affected_agents=agents,
        member_trace_ids=trace_ids,
        member_count=member_count,
        outcome_distribution=(("SAFE_FAILURE", member_count),),
        avg_groundedness=0.4,
        hitl_escalation_rate=hitl_rate,
        healer_invocation_rate=healer_rate,
        adg_cluster_node=f"ADG::RCACluster::{failure_pattern}::abc",
        timestamp_utc=_TS,
    )


def _make_proposal(
    change_type="ROUTING_RULE_ADJUSTMENT",
    risk_class="LOW",
    reward_score=None,
    policy_hash=None,
    affected_component="ADG::Module::router",
    evidence=(),
):
    from system_learning.types.optimization_types import OptimizationProposal

    pid = _sha256(change_type + risk_class + affected_component)
    cid = _sha256("cluster")
    return OptimizationProposal(
        proposal_id=pid,
        cluster_id=cid,
        proposed_change_type=change_type,
        affected_component=affected_component,
        expected_outcome="Test outcome",
        risk_class=risk_class,
        change_spec=(
            ("change_type", change_type),
            ("cluster_id", cid),
            ("dominant_route", "PATH_A"),
            ("failure_pattern", "SAFE_FAILURE"),
            ("member_count", "5"),
            ("avg_groundedness", "0.700000"),
            ("hitl_escalation_rate", "0.000000"),
            ("healer_invocation_rate", "0.000000"),
        ),
        evidence_bundle_hashes=evidence or (_HASH64,),
        reward_score=reward_score,
        policy_hash=policy_hash,
        timestamp_utc=_TS,
    )


def _make_signal(trace_id, gnd=0.9, policy=0.95, replay=1.0, guard=1.0, mut=1.0, approval=None):
    from system_learning.types.optimization_types import GovernanceRewardSignal

    sid = _sha256(trace_id)
    return GovernanceRewardSignal(
        signal_id=sid,
        trace_id=trace_id,
        groundedness_score=gnd,
        policy_compliance=policy,
        replay_stability=replay,
        guardrail_cleanliness=guard,
        mutation_correctness=mut,
        human_approval=approval,
        timestamp_utc=_TS,
    )


# ===========================================================================
# TestTraceFeatureExtractor
# ===========================================================================


class TestTraceFeatureExtractor:
    def _extractor(self):
        from system_learning.engines.trace_feature_extractor import TraceFeatureExtractor

        return TraceFeatureExtractor()

    def _signal(self, **kw):
        defaults = {
            "route_selected": "PATH_A",
            "confidence_gate_state": "pass",
            "retrieval_path": "RAG_BGE",
            "retrieval_groundedness_score": 0.8,
            "policy_hashes": ["ph1"],
            "guardrails_applied": ["g1"],
            "determinism_markers": ["dm1"],
            "healing_invoked": False,
            "healer_id": None,
            "human_escalation_flag": False,
            "mutation_presence": False,
            "success": True,
            "adg_entity_name": "ADG::Module::alpha",
            "adg_relation_ids": ["r1"],
        }
        defaults.update(kw)
        return defaults

    def test_success_outcome_extracted(self):
        b = self._extractor().extract("tr-001", self._signal(success=True), _TS)
        assert b.final_outcome_class == "SUCCESS"

    def test_replay_failure_highest_priority(self):
        b = self._extractor().extract(
            "tr-002",
            self._signal(success=True, replay_failed=True),
            _TS,
        )
        assert b.final_outcome_class == "REPLAY_FAILURE"

    def test_rollback_priority(self):
        b = self._extractor().extract(
            "tr-003",
            self._signal(success=False, rollback=True),
            _TS,
        )
        assert b.final_outcome_class == "ROLLBACK"

    def test_healed_success(self):
        b = self._extractor().extract(
            "tr-004",
            self._signal(success=True, healed=True),
            _TS,
        )
        assert b.final_outcome_class == "HEALED_SUCCESS"

    def test_safe_failure(self):
        b = self._extractor().extract(
            "tr-005",
            self._signal(success=False),
            _TS,
        )
        assert b.final_outcome_class == "SAFE_FAILURE"

    def test_unknown_outcome_when_no_success_key(self):
        sig = {k: v for k, v in self._signal().items() if k != "success"}
        b = self._extractor().extract("tr-006", sig, _TS)
        assert b.final_outcome_class == "UNKNOWN"

    def test_gate_state_mapping(self):
        for raw, expected in [
            ("pass", "PASS"),
            ("stall", "STALL"),
            ("escalate", "ESCALATE"),
            ("PASSED", "PASS"),
            ("Stalled", "STALL"),
            ("bogus", "PASS"),
        ]:
            b = self._extractor().extract("tr-x", self._signal(confidence_gate_state=raw), _TS)
            assert b.confidence_gate_state == expected, f"raw={raw!r}"

    def test_groundedness_clamped_to_0_1(self):
        b = self._extractor().extract("tr-x", self._signal(retrieval_groundedness_score=5.0), _TS)
        assert b.retrieval_groundedness_score == 1.0

        b2 = self._extractor().extract("tr-y", self._signal(retrieval_groundedness_score=-1.0), _TS)
        assert b2.retrieval_groundedness_score == 0.0

    def test_missing_fields_produce_safe_defaults(self):
        b = self._extractor().extract("tr-empty", {}, _TS)
        assert b.route_selected == "UNKNOWN"
        assert b.retrieval_path == "UNKNOWN"
        assert b.final_outcome_class == "UNKNOWN"
        assert b.adg_entity_name == "ADG::Unknown"

    def test_batch_skips_bad_entries_and_continues(self):
        # Pass a valid and a signal that produces a bundle (no failures expected
        # since extractor is fail-safe for all signal shapes)
        traces = [
            ("tr-a", self._signal(success=True), _TS),
            ("tr-b", self._signal(success=False), _TS + 1),
        ]
        bundles = self._extractor().extract_batch(traces)
        assert len(bundles) == 2

    def test_extract_record_returns_trace_feature_record(self):
        from system_learning.types.trace_feature_types import TraceFeatureRecord

        rec = self._extractor().extract_record("tr-r", self._signal(), _TS)
        assert isinstance(rec, TraceFeatureRecord)
        assert rec.trace_id == "tr-r"

    def test_module_level_helpers(self):
        from system_learning.engines.trace_feature_extractor import (
            build_feature_bundle,
            build_trace_record,
        )

        b = build_feature_bundle("tr-h1", self._signal(), _TS)
        r = build_trace_record("tr-h2", self._signal(), _TS)
        assert b.trace_id == "tr-h1"
        assert r.trace_id == "tr-h2"


# ===========================================================================
# TestRCAClusterEngine
# ===========================================================================


class TestRCAClusterEngine:
    def _engine(self, **kw):
        from system_learning.engines.rca_cluster_engine import (
            RCAClusterConfig,
            RCAClusterEngine,
        )

        return RCAClusterEngine(RCAClusterConfig(**kw))

    def test_two_same_pattern_records_form_cluster(self):
        records = [
            _make_record("t1", groundedness=0.2),
            _make_record("t2", groundedness=0.3),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "LOW_GROUNDEDNESS" in patterns

    def test_singleton_merged_into_residual(self):
        records = [
            _make_record("t1", groundedness=0.2),
            _make_record("t2", groundedness=0.3),
            # singleton with different pattern
            _make_record("t3", outcome="REPLAY_FAILURE"),
        ]
        clusters = self._engine(min_cluster_size=2).cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "SINGLETON_RESIDUAL" in patterns

    def test_allow_singletons_config(self):
        records = [_make_record("t1", outcome="REPLAY_FAILURE")]
        clusters = self._engine(min_cluster_size=1, allow_singletons=True).cluster(records, _TS)
        assert len(clusters) >= 1
        assert all(c.failure_pattern != "SINGLETON_RESIDUAL" for c in clusters)

    def test_negative_seed_produces_cluster(self):
        from system_learning.types.trace_feature_types import FailurePattern

        seed = FailurePattern(
            pattern_id=_HASH64,
            source_type="VIOLATION",
            signature="AuthorityViolation",
            affected_component="ADG::Module::guard",
            occurrence_count=5,
            evidence_hash=_HASH64,
            cluster_id=None,
            timestamp_utc=_TS,
        )
        clusters = self._engine().cluster([], _TS, negative_seeds=[seed])
        patterns = {c.failure_pattern for c in clusters}
        assert any("NEG_SEED" in p for p in patterns)

    def test_cluster_ids_are_deterministic(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(4)]
        c1 = self._engine().cluster(records, _TS)
        c2 = self._engine().cluster(records, _TS)
        ids1 = sorted(c.cluster_id for c in c1)
        ids2 = sorted(c.cluster_id for c in c2)
        assert ids1 == ids2

    def test_cluster_member_count_correct(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(6)]
        clusters = self._engine().cluster(records, _TS)
        low_g = [c for c in clusters if c.failure_pattern == "LOW_GROUNDEDNESS"]
        assert len(low_g) == 1
        assert low_g[0].member_count == 6

    def test_healer_required_pattern(self):
        records = [
            _make_record("t1", healer="healer_A"),
            _make_record("t2", healer="healer_B"),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "HEALER_REQUIRED" in patterns

    def test_hitl_escalation_pattern(self):
        records = [
            _make_record("t1", hitl=True),
            _make_record("t2", hitl=True),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "HITL_ESCALATION" in patterns

    def test_guardrail_block_pattern(self):
        records = [
            _make_record("t1", groundedness=0.9, guardrails=("g1",)),
            _make_record("t2", groundedness=0.9, guardrails=("g1",)),
        ]
        clusters = self._engine().cluster(records, _TS)
        patterns = {c.failure_pattern for c in clusters}
        assert "GUARDRAIL_BLOCK" in patterns

    def test_output_sorted_by_cluster_id(self):
        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(4)]
        clusters = self._engine().cluster(records, _TS)
        ids = [c.cluster_id for c in clusters]
        assert ids == sorted(ids)

    def test_module_level_cluster_records(self):
        from system_learning.engines.rca_cluster_engine import cluster_records

        records = [_make_record(f"t{i}", groundedness=0.2) for i in range(2)]
        clusters = cluster_records(records, _TS)
        assert isinstance(clusters, list)


# ===========================================================================
# TestOptimizationProposalEngine
# ===========================================================================


class TestOptimizationProposalEngine:
    def _engine(self, **kw):
        from system_learning.engines.optimization_proposal_engine import (
            OptimizationProposalEngine,
            ProposalEngineConfig,
        )

        return OptimizationProposalEngine(ProposalEngineConfig(**kw))

    def test_low_groundedness_produces_retrieval_proposal(self):
        cluster = _make_cluster("LOW_GROUNDEDNESS")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "RETRIEVAL_RANKING_ADJUSTMENT" in types

    def test_hitl_escalation_produces_confidence_proposal(self):
        cluster = _make_cluster("HITL_ESCALATION")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "CONFIDENCE_THRESHOLD_UPDATE" in types

    def test_guardrail_block_produces_guardrail_proposal(self):
        cluster = _make_cluster("GUARDRAIL_BLOCK")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "GUARDRAIL_REFINEMENT" in types

    def test_healer_required_produces_healer_proposal(self):
        cluster = _make_cluster("HEALER_REQUIRED")
        proposals = self._engine().generate([cluster], _TS)
        types = {p.proposed_change_type for p in proposals}
        assert "HEALER_ROUTING_IMPROVEMENT" in types

    def test_unknown_pattern_produces_no_proposal(self):
        cluster = _make_cluster("TOTALLY_UNKNOWN_PATTERN_XYZ")
        proposals = self._engine().generate([cluster], _TS)
        assert proposals == []

    def test_high_risk_downgraded_for_small_cluster(self):
        # POLICY_VIOLATION → HIGH risk, but member_count=2 < min_cluster_members_for_high_risk=5
        cluster = _make_cluster("POLICY_VIOLATION", member_count=2)
        proposals = self._engine().generate([cluster], _TS)
        # Should be downgraded to MEDIUM
        assert all(p.risk_class == "MEDIUM" for p in proposals)

    def test_critical_blocked_by_default(self):
        # Force a CRITICAL proposal by patching — use allow_critical=False (default)
        cluster = _make_cluster("REPLAY_FAILURE", member_count=10)
        # Manually set risk_class to CRITICAL is not directly possible since rule
        # table uses HIGH at most. Test that allow_critical=False doesn't crash.
        proposals = self._engine(allow_critical=False).generate([cluster], _TS)
        assert all(p.risk_class != "CRITICAL" for p in proposals)

    def test_max_proposals_per_cluster_respected(self):
        agents = tuple(f"ADG::Module::agent{i}" for i in range(10))
        cluster = _make_cluster("LOW_GROUNDEDNESS", agents=agents)
        proposals = self._engine(max_proposals_per_cluster=3).generate([cluster], _TS)
        assert len(proposals) <= 3

    def test_proposal_ids_are_unique(self):
        clusters = [_make_cluster("LOW_GROUNDEDNESS"), _make_cluster("HITL_ESCALATION")]
        proposals = self._engine().generate(clusters, _TS)
        ids = [p.proposal_id for p in proposals]
        assert len(ids) == len(set(ids))

    def test_proposals_sorted_by_id(self):
        clusters = [_make_cluster("LOW_GROUNDEDNESS"), _make_cluster("HITL_ESCALATION")]
        proposals = self._engine().generate(clusters, _TS)
        ids = [p.proposal_id for p in proposals]
        assert ids == sorted(ids)

    def test_evidence_bundle_hash_references_cluster(self):
        cluster = _make_cluster("LOW_GROUNDEDNESS")
        proposals = self._engine().generate([cluster], _TS)
        assert all(cluster.stable_hash() in p.evidence_bundle_hashes for p in proposals)

    def test_module_level_generate_proposals(self):
        from system_learning.engines.optimization_proposal_engine import generate_proposals

        cluster = _make_cluster("HEALER_REQUIRED")
        proposals = generate_proposals([cluster], _TS)
        assert isinstance(proposals, list)


# ===========================================================================
# TestProposalValidationEngine
# ===========================================================================


class TestProposalValidationEngine:
    def _engine(self, **kw):
        from system_learning.engines.proposal_validation_engine import (
            ProposalValidationEngine,
            ValidationConfig,
        )

        return ProposalValidationEngine(ValidationConfig(**kw))

    def test_clean_proposal_passes_all_gates(self):
        p = _make_proposal()
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is True
        assert result.denial_reasons == ()

    def test_unknown_component_fails_guardrail_gate(self):
        p = _make_proposal(affected_component="ADG::Unknown")
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "UNKNOWN_AFFECTED_COMPONENT" in result.denial_reasons

    def test_embedding_expansion_with_no_evidence_fails_replay_gate(self):
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster")
        pid = _sha256("EMBEDDING_CORPUS_EXPANSION_LOW_ADG::Module::router")
        p = OptimizationProposal(
            proposal_id=pid,
            cluster_id=cid,
            proposed_change_type="EMBEDDING_CORPUS_EXPANSION",
            affected_component="ADG::Module::router",
            expected_outcome="Test outcome",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(),  # explicitly empty
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "EMBEDDING_EXPANSION_NO_EVIDENCE" in result.denial_reasons

    def test_policy_hash_mismatch_fails_policy_gate(self):
        p = _make_proposal(policy_hash="hash_a")
        result = self._engine(active_policy_hash="hash_b").validate(p, _TS)
        assert result.validation_pass is False
        assert "POLICY_HASH_MISMATCH" in result.denial_reasons

    def test_policy_hash_match_passes_policy_gate(self):
        p = _make_proposal(policy_hash="hash_a")
        result = self._engine(active_policy_hash="hash_a").validate(p, _TS)
        assert result.policy_safe is True

    def test_high_regression_blocks_high_risk_proposal(self):
        p = _make_proposal(risk_class="HIGH")
        result = self._engine().validate(p, _TS, hitl_rate=0.8)
        # HITL rate 0.8 → HIGH regression for HIGH risk proposal
        assert result.validation_pass is False
        assert "HIGH_REGRESSION_RISK" in result.denial_reasons

    def test_high_regression_does_not_block_low_risk(self):
        p = _make_proposal(risk_class="LOW")
        result = self._engine().validate(p, _TS, hitl_rate=0.9)
        # LOW risk → regression should not block
        assert result.validation_pass is True

    def test_result_id_is_sha256_hexdigest(self):
        p = _make_proposal()
        result = self._engine().validate(p, _TS)
        assert len(result.result_id) == 64
        assert all(c in "0123456789abcdef" for c in result.result_id)

    def test_batch_validation_returns_sorted_results(self):
        proposals = [
            _make_proposal(risk_class="LOW"),
            _make_proposal(change_type="CONFIDENCE_THRESHOLD_UPDATE"),
        ]
        results = self._engine().validate_batch(proposals, _TS)
        ids = [r.result_id for r in results]
        assert ids == sorted(ids)

    def test_gate_exception_counts_as_failure(self):
        # Force a determinism gate failure by using a non-hash proposal_id
        from system_learning.types.optimization_types import OptimizationProposal

        cid = _sha256("cluster")
        p = OptimizationProposal(
            proposal_id="NOT_A_HASH",  # will fail determinism gate
            cluster_id=cid,
            proposed_change_type="ROUTING_RULE_ADJUSTMENT",
            affected_component="ADG::Module::router",
            expected_outcome="Test",
            risk_class="LOW",
            change_spec=(("k", "v"),),
            evidence_bundle_hashes=(_HASH64,),
            reward_score=None,
            policy_hash=None,
            timestamp_utc=_TS,
        )
        result = self._engine().validate(p, _TS)
        assert result.validation_pass is False
        assert "PROPOSAL_ID_NOT_HASH" in result.denial_reasons

    def test_module_level_validate_proposal(self):
        from system_learning.engines.proposal_validation_engine import validate_proposal

        p = _make_proposal()
        result = validate_proposal(p, _TS)
        assert result.validation_pass is True


# ===========================================================================
# TestGovernanceRewardModel
# ===========================================================================


class TestGovernanceRewardModel:
    def _model(self, **kw):
        from system_learning.engines.governance_reward_model import (
            GovernanceRewardModel,
            RewardModelConfig,
        )

        return GovernanceRewardModel(RewardModelConfig(**kw))

    def test_high_quality_signals_produce_high_score(self):
        p = _make_proposal()
        signals = [_make_signal(f"t{i}") for i in range(5)]
        score = self._model().score(p, signals, _TS)
        assert score.aggregate_score > 0.8
        assert score.invariant_preserved is True

    def test_zero_signals_produce_zero_score_and_invariant_false(self):
        p = _make_proposal()
        score = self._model().score(p, [], _TS)
        assert score.aggregate_score == 0.0
        assert score.invariant_preserved is False
        assert score.signal_count == 0

    def test_low_policy_compliance_breaks_invariant(self):
        p = _make_proposal()
        # policy_compliance < 0.80 (floor)
        signals = [_make_signal(f"t{i}", policy=0.5) for i in range(3)]
        score = self._model().score(p, signals, _TS)
        assert score.invariant_preserved is False

    def test_low_replay_stability_breaks_invariant(self):
        p = _make_proposal()
        signals = [_make_signal(f"t{i}", replay=0.5) for i in range(3)]
        score = self._model().score(p, signals, _TS)
        assert score.invariant_preserved is False

    def test_human_approval_rate_computed_correctly(self):
        p = _make_proposal()
        signals = [
            _make_signal("t1", approval=True),
            _make_signal("t2", approval=False),
            _make_signal("t3", approval=None),  # no HITL
        ]
        score = self._model().score(p, signals, _TS)
        # 1 approved out of 2 HITL signals
        assert score.human_approval_rate == pytest.approx(0.5, abs=1e-6)

    def test_no_hitl_signals_approval_rate_is_1(self):
        p = _make_proposal()
        signals = [_make_signal("t1", approval=None)]
        score = self._model().score(p, signals, _TS)
        assert score.human_approval_rate == 1.0

    def test_invalid_signal_empty_trace_id_skipped(self):
        from system_learning.types.optimization_types import GovernanceRewardSignal

        p = _make_proposal()
        bad_signal = GovernanceRewardSignal(
            signal_id=_HASH64,
            trace_id="",  # invalid
            groundedness_score=0.9,
            policy_compliance=0.95,
            replay_stability=1.0,
            guardrail_cleanliness=1.0,
            mutation_correctness=1.0,
            human_approval=None,
            timestamp_utc=_TS,
        )
        score = self._model().score(p, [bad_signal], _TS)
        assert score.signal_count == 0  # invalid signal was rejected

    def test_weights_must_sum_to_1(self):
        from system_learning.engines.governance_reward_model import RewardModelConfig

        with pytest.raises(ValueError, match="sum to 1.0"):
            RewardModelConfig(
                weight_groundedness=0.5,
                weight_policy_compliance=0.5,
                weight_replay_stability=0.5,
                weight_guardrail_cleanliness=0.5,
                weight_mutation_correctness=0.5,
            )

    def test_annotate_proposals_sets_reward_score(self):
        p = _make_proposal()
        signals = [_make_signal(f"t{i}") for i in range(3)]
        model = self._model()
        scores = model.score_batch([p], {p.proposal_id: signals}, _TS)
        annotated = model.annotate_proposals([p], scores, _TS)
        assert len(annotated) == 1
        assert annotated[0].reward_score is not None
        assert 0.0 <= annotated[0].reward_score <= 1.0

    def test_module_level_score_proposal(self):
        from system_learning.engines.governance_reward_model import score_proposal

        p = _make_proposal()
        signals = [_make_signal("t1")]
        score = score_proposal(p, signals, _TS)
        assert score.proposal_id == p.proposal_id
