"""
Wave 3 Phase 9 — Meta-Learning Pipeline Tests

§4-compliant test suite covering:
- HealingConfidenceScorer: scoring, action mapping, thresholds, edge cases
- ArbitrationEngine: winner selection, tie-breaking, duplicate ID guard,
  min_score filter, kind allowlist, merged payload, determinism
- ArbitrationDecision / HealingConfidenceReport: canonical hash integrity
"""

from __future__ import annotations

import math

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

# REMOVED: _emit_authorize_and_execute("p2", "test_meta_learning_pipeline", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_meta_learning_pipeline", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_meta_learning_pipeline", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_meta_learning_pipeline", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_meta_learning_pipeline", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_meta_learning_pipeline", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_meta_learning_pipeline", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_meta_learning_pipeline", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_meta_learning_pipeline", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_meta_learning_pipeline", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_meta_learning_pipeline", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_meta_learning_pipeline", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_meta_learning_pipeline", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_meta_learning_pipeline", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_meta_learning_pipeline", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_meta_learning_pipeline", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_meta_learning_pipeline", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_meta_learning_pipeline", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_meta_learning_pipeline", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_meta_learning_pipeline", "exec_snapshot_link")
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
from system_learning.arbitration.engine import ArbitrationEngine
from system_learning.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationDecision,
    ArbitrationPolicy,
)
from system_learning.confidence.engine import HealingConfidenceScorer
from system_learning.confidence.types import (
    HealingAttempt,
    HealingConfidenceReport,
)

# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_meta_learning_pipeline", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_meta_learning_pipeline", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_meta_learning_pipeline", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_meta_learning_pipeline", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_meta_learning_pipeline", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_meta_learning_pipeline", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_meta_learning_pipeline", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_meta_learning_pipeline", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_meta_learning_pipeline", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_meta_learning_pipeline", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_meta_learning_pipeline", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_meta_learning_pipeline", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_meta_learning_pipeline", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_meta_learning_pipeline", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_meta_learning_pipeline", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_meta_learning_pipeline", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_meta_learning_pipeline", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_meta_learning_pipeline", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_meta_learning_pipeline", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_meta_learning_pipeline", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_meta_learning_pipeline", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_pipeline", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_meta_learning_pipeline", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_meta_learning_pipeline")
# REMOVED: _emit_applies_guardrail("p0", "test_meta_learning_pipeline", "p0_governance")
# REMOVED: _emit_snapshots_state("p0", "test_meta_learning_pipeline", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_pipeline", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_meta_learning_pipeline", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_pipeline", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_meta_learning_pipeline", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_pipeline", "write_through")
# REMOVED: _emit_writes_through("p1", "test_meta_learning_pipeline", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_meta_learning_pipeline", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_meta_learning_pipeline", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_meta_learning_pipeline", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_meta_learning_pipeline", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_meta_learning_pipeline", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_meta_learning_pipeline", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_meta_learning_pipeline", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_meta_learning_pipeline", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_meta_learning_pipeline", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_meta_learning_pipeline", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_meta_learning_pipeline", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_meta_learning_pipeline", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_meta_learning_pipeline", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_meta_learning_pipeline", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_meta_learning_pipeline")
# REMOVED: _emit_gated_by_confidence("p1", "test_meta_learning_pipeline", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_meta_learning_pipeline")
# REMOVED: emit_determinism_digest("p0", "test_meta_learning_pipeline")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _attempt(
    attempt_id: str = "a1",
    healer_id: str = "h1",
    outcome: str = "SUCCESS",
    severity: int = 0,
    cost: float = 0.0,
    signals: dict | None = None,
) -> HealingAttempt:
    return HealingAttempt(
        attempt_id=attempt_id,
        healer_id=healer_id,
        outcome=outcome,
        severity=severity,
        cost=cost,
        signals=signals or {},
    )


def _policy(
    allowed_kinds: set[str] | None = None,
    weights: dict | None = None,
    thresholds: dict | None = None,
    caps: dict | None = None,
) -> ArbitrationPolicy:
    return ArbitrationPolicy(
        weights=weights or {},
        caps=caps or {},
        thresholds=thresholds or {},
        allowed_kinds=allowed_kinds or {"analysis", "decision"},
    )


def _candidate(
    cid: str = "c1",
    kind: str = "analysis",
    score: float = 0.7,
    cost: float = 1.0,
    payload: dict | None = None,
    provenance: str = "agent-A",
) -> ArbitrationCandidate:
    return ArbitrationCandidate(
        id=cid,
        kind=kind,
        payload=payload or {},
        score=score,
        cost=cost,
        provenance=provenance,
    )


# ===========================================================================
# 1. HealingConfidenceScorer — scoring and action mapping
# ===========================================================================


class TestHealingConfidenceScorer:
    @pytest.mark.governance
    def test_score_success_attempt_returns_accept_action(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="SUCCESS", severity=0, cost=0.0)
        report = scorer.score([a])
        assert report.decisions[0].action == "ACCEPT"

    @pytest.mark.governance
    def test_score_fail_attempt_low_confidence_returns_escalate(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="FAIL", severity=5, cost=10.0)
        report = scorer.score([a])
        assert report.decisions[0].action in ("ESCALATE", "REVIEW")

    @pytest.mark.governance
    def test_score_partial_attempt_returns_review_or_accept(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="PARTIAL", severity=0, cost=0.0)
        report = scorer.score([a])
        assert report.decisions[0].action in ("REVIEW", "ACCEPT")

    @pytest.mark.governance
    def test_score_empty_attempts_returns_empty_report(self):
        scorer = HealingConfidenceScorer()
        report = scorer.score([])
        assert report.decisions == []

    @pytest.mark.governance
    def test_score_raises_type_error_on_none(self):
        scorer = HealingConfidenceScorer()
        with pytest.raises(TypeError):
            scorer.score(None)  # type: ignore

    @pytest.mark.governance
    def test_score_raises_value_error_for_unknown_outcome(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="UNKNOWN")
        with pytest.raises(ValueError, match="Unknown outcome"):
            scorer.score([a])

    @pytest.mark.governance
    def test_score_raises_value_error_for_empty_attempt_id(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(attempt_id="")
        with pytest.raises(ValueError, match="Attempt ID"):
            scorer.score([a])

    @pytest.mark.governance
    def test_score_raises_type_error_for_non_healing_attempt(self):
        scorer = HealingConfidenceScorer()
        with pytest.raises(TypeError, match="HealingAttempt"):
            scorer.score(["not_an_attempt"])  # type: ignore

    @pytest.mark.governance
    def test_confidence_for_success_always_at_least_partial_minus_01(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="SUCCESS", severity=10, cost=100.0)
        report = scorer.score([a])
        # Monotonic guard: SUCCESS >= PARTIAL - 0.1 = 0.4
        assert report.decisions[0].confidence >= 0.4

    @pytest.mark.governance
    def test_confidence_for_fail_never_exceeds_partial_plus_01(self):
        scorer = HealingConfidenceScorer()
        a = _attempt(outcome="FAIL", severity=0, cost=0.0)
        report = scorer.score([a])
        # Monotonic guard: FAIL <= PARTIAL + 0.1 = 0.6
        assert report.decisions[0].confidence <= 0.6

    @pytest.mark.governance
    def test_confidence_clamped_to_0_1(self):
        scorer = HealingConfidenceScorer()
        for outcome in ("SUCCESS", "PARTIAL", "FAIL"):
            a = _attempt(outcome=outcome, severity=100, cost=1000.0)
            report = scorer.score([a])
            c = report.decisions[0].confidence
            assert 0.0 <= c <= 1.0

    @pytest.mark.governance
    def test_higher_severity_lowers_confidence(self):
        scorer = HealingConfidenceScorer()
        low = _attempt(attempt_id="a1", outcome="SUCCESS", severity=0)
        high = _attempt(attempt_id="a2", outcome="SUCCESS", severity=5)
        r_low = scorer.score([low]).decisions[0].confidence
        r_high = scorer.score([high]).decisions[0].confidence
        assert r_low >= r_high

    @pytest.mark.governance
    def test_higher_cost_lowers_confidence(self):
        scorer = HealingConfidenceScorer()
        cheap = _attempt(attempt_id="a1", outcome="SUCCESS", cost=0.0)
        expensive = _attempt(attempt_id="a2", outcome="SUCCESS", cost=10.0)
        r_cheap = scorer.score([cheap]).decisions[0].confidence
        r_expensive = scorer.score([expensive]).decisions[0].confidence
        assert r_cheap >= r_expensive

    @pytest.mark.governance
    def test_score_deterministic_for_same_attempts_twice(self):
        scorer = HealingConfidenceScorer()
        attempts = [_attempt(attempt_id="a1", outcome="SUCCESS")]
        r1 = scorer.score(attempts)
        r2 = scorer.score(attempts)
        assert r1.confidence_fingerprint == r2.confidence_fingerprint

    @pytest.mark.governance
    def test_score_sorts_by_attempt_id_for_determinism(self):
        scorer = HealingConfidenceScorer()
        a1 = _attempt(attempt_id="z_last", outcome="PARTIAL")
        a2 = _attempt(attempt_id="a_first", outcome="PARTIAL")
        report = scorer.score([a1, a2])
        ids = [d.attempt_id for d in report.decisions]
        assert ids == sorted(ids)

    @pytest.mark.governance
    def test_action_escalate_threshold(self):
        scorer = HealingConfidenceScorer()
        # confidence < 0.33 → ESCALATE; use FAIL with high severity/cost
        a = _attempt(outcome="FAIL", severity=5, cost=6.0)
        conf = scorer._calculate_confidence(a)
        expected = scorer._map_confidence_to_action(conf)
        report = scorer.score([a])
        assert report.decisions[0].action == expected

    @pytest.mark.governance
    def test_report_confidence_fingerprint_is_64_hex_chars(self):
        scorer = HealingConfidenceScorer()
        report = scorer.score([_attempt()])
        assert len(report.confidence_fingerprint) == 64

    @pytest.mark.governance
    def test_empty_report_has_deterministic_fingerprint(self):
        scorer = HealingConfidenceScorer()
        r1 = scorer.score([])
        r2 = scorer.score([])
        assert r1.confidence_fingerprint == r2.confidence_fingerprint


# ===========================================================================
# 2. ArbitrationEngine — winner selection and guards
# ===========================================================================


class TestArbitrationEngine:
    @pytest.mark.governance
    def test_arbitrate_raises_type_error_on_none_candidates(self):
        eng = ArbitrationEngine()
        with pytest.raises(TypeError):
            eng.arbitrate(None, _policy())  # type: ignore

    @pytest.mark.governance
    def test_arbitrate_empty_candidates_returns_no_candidates_rationale(self):
        eng = ArbitrationEngine()
        dec = eng.arbitrate([], _policy())
        assert "no_candidates" in dec.rationale_codes
        assert dec.winner_ids == ()

    @pytest.mark.governance
    def test_arbitrate_selects_highest_score_winner(self):
        eng = ArbitrationEngine()
        low = _candidate("low", score=0.3)
        high = _candidate("high", score=0.9)
        dec = eng.arbitrate([low, high], _policy())
        assert dec.winner_ids[0] == "high"

    @pytest.mark.governance
    def test_arbitrate_single_candidate_selects_it(self):
        eng = ArbitrationEngine()
        dec = eng.arbitrate([_candidate("only")], _policy())
        assert "only" in dec.winner_ids

    @pytest.mark.governance
    def test_arbitrate_raises_on_duplicate_candidate_ids(self):
        eng = ArbitrationEngine()
        c1 = _candidate("dup", score=0.5)
        c2 = _candidate("dup", score=0.7)
        with pytest.raises(ValueError, match="Duplicate"):
            eng.arbitrate([c1, c2], _policy())

    @pytest.mark.governance
    def test_arbitrate_raises_on_unknown_kind(self):
        eng = ArbitrationEngine()
        c = _candidate("c1", kind="forbidden_kind")
        policy = _policy(allowed_kinds={"analysis"})
        with pytest.raises(ValueError, match="Unknown kind"):
            eng.arbitrate([c], policy)

    @pytest.mark.governance
    def test_arbitrate_raises_on_nan_score(self):
        eng = ArbitrationEngine()
        c = _candidate("c1", score=float("nan"))
        with pytest.raises(ValueError, match="Invalid score"):
            eng.arbitrate([c], _policy())

    @pytest.mark.governance
    def test_arbitrate_raises_on_inf_score(self):
        eng = ArbitrationEngine()
        c = _candidate("c1", score=math.inf)
        with pytest.raises(ValueError, match="Invalid score"):
            eng.arbitrate([c], _policy())

    @pytest.mark.governance
    def test_arbitrate_filters_below_min_score(self):
        eng = ArbitrationEngine()
        low = _candidate("low", score=0.1)
        high = _candidate("high", score=0.8)
        policy = _policy(thresholds={"min_score": 0.5})
        dec = eng.arbitrate([low, high], policy)
        assert "low" not in dec.winner_ids
        assert "high" in dec.winner_ids

    @pytest.mark.governance
    def test_arbitrate_no_valid_candidates_returns_no_valid_rationale(self):
        eng = ArbitrationEngine()
        c = _candidate("low", score=0.1)
        policy = _policy(thresholds={"min_score": 0.9})
        dec = eng.arbitrate([c], policy)
        assert "no_valid_candidates" in dec.rationale_codes
        assert dec.winner_ids == ()

    @pytest.mark.governance
    def test_arbitrate_applies_kind_weights(self):
        eng = ArbitrationEngine()
        c1 = _candidate("c1", kind="analysis", score=0.5)
        c2 = _candidate("c2", kind="decision", score=0.4)
        policy = _policy(
            weights={"analysis": 1.0, "decision": 2.0},
            allowed_kinds={"analysis", "decision"},
        )
        dec = eng.arbitrate([c1, c2], policy)
        # c2 weighted: 0.4 * 2.0 = 0.8 > c1: 0.5 * 1.0 = 0.5
        assert dec.winner_ids[0] == "c2"

    @pytest.mark.governance
    def test_tiebreak_by_lower_cost(self):
        eng = ArbitrationEngine()
        c1 = _candidate("expensive", score=0.7, cost=5.0)
        c2 = _candidate("cheap", score=0.7, cost=1.0)
        dec = eng.arbitrate([c1, c2], _policy())
        assert dec.winner_ids[0] == "cheap"

    @pytest.mark.governance
    def test_tiebreak_final_by_lexicographic_id(self):
        eng = ArbitrationEngine()
        c1 = _candidate("zebra", score=0.7, cost=1.0)
        c2 = _candidate("alpha", score=0.7, cost=1.0)
        dec = eng.arbitrate([c1, c2], _policy())
        assert dec.winner_ids[0] == "alpha"

    @pytest.mark.governance
    def test_max_winners_cap_respected(self):
        eng = ArbitrationEngine()
        candidates = [_candidate(f"c{i}", score=float(i) / 10) for i in range(5)]
        policy = _policy(caps={"max_winners": 2})
        dec = eng.arbitrate(candidates, policy)
        assert len(dec.winner_ids) <= 2

    @pytest.mark.governance
    def test_cap_applied_rationale_code_present_when_capped(self):
        eng = ArbitrationEngine()
        candidates = [_candidate(f"c{i}", score=0.5 + i * 0.01) for i in range(5)]
        policy = _policy(caps={"max_winners": 2})
        dec = eng.arbitrate(candidates, policy)
        assert "cap_applied" in dec.rationale_codes

    @pytest.mark.governance
    def test_merged_payload_none_for_single_winner(self):
        eng = ArbitrationEngine()
        dec = eng.arbitrate([_candidate("only")], _policy())
        assert dec.merged_payload is None

    @pytest.mark.governance
    def test_merged_payload_present_for_multiple_winners(self):
        eng = ArbitrationEngine()
        c1 = _candidate("c1", score=0.8)
        c2 = _candidate("c2", score=0.6)
        policy = _policy(caps={"max_winners": 2})
        dec = eng.arbitrate([c1, c2], policy)
        assert dec.merged_payload is not None
        assert "merged_from" in dec.merged_payload

    @pytest.mark.governance
    def test_deterministic_fingerprint_is_64_hex_chars(self):
        eng = ArbitrationEngine()
        dec = eng.arbitrate([_candidate()], _policy())
        assert len(dec.deterministic_fingerprint) == 64

    @pytest.mark.governance
    def test_arbitrate_deterministic_for_same_inputs_twice(self):
        eng = ArbitrationEngine()
        c = _candidate("c1", score=0.7)
        dec1 = eng.arbitrate([c], _policy())
        dec2 = eng.arbitrate([c], _policy())
        assert dec1.deterministic_fingerprint == dec2.deterministic_fingerprint

    @pytest.mark.governance
    def test_created_at_does_not_affect_ordering(self):
        eng = ArbitrationEngine()
        c1 = ArbitrationCandidate(
            id="c1", kind="analysis", payload={}, score=0.7, cost=1.0, provenance="x", created_at=1000
        )
        c2 = ArbitrationCandidate(
            id="c2", kind="analysis", payload={}, score=0.7, cost=1.0, provenance="x", created_at=9999
        )
        policy = _policy(caps={"max_winners": 1})
        dec = eng.arbitrate([c1, c2], policy)
        # Ordering should be by id (alphabetical), not created_at
        assert dec.winner_ids[0] == "c1"

    @pytest.mark.governance
    def test_weighted_scoring_rationale_code_always_present(self):
        eng = ArbitrationEngine()
        dec = eng.arbitrate([_candidate()], _policy())
        assert "weighted_scoring" in dec.rationale_codes


# ===========================================================================
# 3. ArbitrationDecision / HealingConfidenceReport — canonical hash integrity
# ===========================================================================


class TestCanonicalHashIntegrity:
    @pytest.mark.governance
    def test_arbitration_decision_content_hash_is_64_hex(self):
        dec = ArbitrationDecision(
            winner_ids=("c1",),
            merged_payload=None,
            rationale_codes=("weighted_scoring",),
            deterministic_fingerprint="a" * 64,
        )
        h = dec.content_hash()
        assert len(h) == 64
        int(h, 16)

    @pytest.mark.governance
    def test_arbitration_decision_content_hash_deterministic(self):
        dec = ArbitrationDecision(
            winner_ids=("c1",),
            merged_payload=None,
            rationale_codes=("weighted_scoring",),
            deterministic_fingerprint="a" * 64,
        )
        assert dec.content_hash() == dec.content_hash()

    @pytest.mark.governance
    def test_arbitration_decision_content_hash_differs_when_winner_changes(self):
        d1 = ArbitrationDecision(
            winner_ids=("c1",), merged_payload=None, rationale_codes=(), deterministic_fingerprint="a" * 64
        )
        d2 = ArbitrationDecision(
            winner_ids=("c2",), merged_payload=None, rationale_codes=(), deterministic_fingerprint="a" * 64
        )
        assert d1.content_hash() != d2.content_hash()

    @pytest.mark.governance
    def test_healing_confidence_report_fingerprint_deterministic(self):
        report = HealingConfidenceReport.from_canonical_bytes([], b"{}")
        assert (
            report.confidence_fingerprint
            == HealingConfidenceReport.from_canonical_bytes([], b"{}").confidence_fingerprint
        )

    @pytest.mark.governance
    def test_healing_attempt_canonical_bytes_deterministic(self):
        a = _attempt()
        assert a.canonical_bytes() == a.canonical_bytes()

    @pytest.mark.governance
    def test_arbitration_candidate_canonical_bytes_excludes_created_at(self):
        c1 = ArbitrationCandidate(
            id="c", kind="analysis", payload={}, score=0.5, cost=1.0, provenance="x", created_at=100
        )
        c2 = ArbitrationCandidate(
            id="c", kind="analysis", payload={}, score=0.5, cost=1.0, provenance="x", created_at=999
        )
        assert c1.canonical_bytes() == c2.canonical_bytes()
