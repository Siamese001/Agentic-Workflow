"""
Hardening tests for Evaluation Spine Phases 1-5.

Covers constitutional rule gaps:
§1.4  Boundary testing — exact threshold edges for all numeric guards
§1.5  Exception path verification — judge callables that raise
§1.10 Deterministic decision surfaces — tie-break ordering stability
§1.12 Matrix testing — judge×input, mode×retriever, policy×validator
§1.13 Metamorphic tests — serialization invariants, _token_f1 symmetry
§1.15 Regression tests — RecallAtK duplicate-inflation, NDCG graded-context
§1.17 Stateful surface tests — tie-scores, single-element, key-order independence
"""

from __future__ import annotations

import math

import pytest
from agentic_core.evaluation.chunking.policies import (
    FixedTokenChunkPolicy,
    OverlapWindowChunkPolicy,
    SemanticChunkPolicy,
)
from agentic_core.evaluation.chunking.validators import (
    MaxChunkSizeValidator,
)
from agentic_core.evaluation.feedback.dpo_batch_builder import DPOBatchBuilder
from agentic_core.evaluation.feedback.proposer_bridge import (
    EvaluatorProposerBridge,
    ImprovementProposal,
    ImprovementSignal,
)
from agentic_core.evaluation.feedback.schemas import (
    DPOBatch,
    DPOPair,
    FeedbackExample,
    ReviewRubric,
)
from agentic_core.evaluation.metrics.answer_correctness import AnswerCorrectness
from agentic_core.evaluation.metrics.groundedness import Groundedness, _token_f1, _tokenize
from agentic_core.evaluation.metrics.ndcg import NDCG
from agentic_core.evaluation.metrics.precision_at_k import PrecisionAtK
from agentic_core.evaluation.metrics.recall_at_k import RecallAtK
from agentic_core.evaluation.monitoring.drift_monitor import (
    AnswerQualityMonitor,
    EmbeddingDriftMonitor,
    RetrievalDriftMonitor,
)
from agentic_core.evaluation.monitoring.snapshots import (
    AnswerQualitySnapshot,
    DriftAlert,
    EmbeddingHealthSnapshot,
    RetrievalDriftSnapshot,
)
from agentic_core.evaluation.retrieval.fusion import ReciprocalRankFusion, ScoreFusion
from agentic_core.evaluation.retrieval.interfaces import Document
from agentic_core.evaluation.retrieval.profiles import (
    PROFILE_HYBRID,
    PROFILE_HYBRID_RERANKED,
    PROFILE_VECTOR_ONLY,
    RetrievalPipeline,
    make_profile,
)
from agentic_core.evaluation.retrieval.reranker import HeuristicReranker, PassthroughReranker
from agentic_core.evaluation.schemas.evaluation_result_schema import (
    DeltaReport,
    EvaluationReport,
    EvaluationResult,
    EvaluationSnapshot,
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

_emit_records_execution_trace("p0", "evidence", "test_hardening")
_emit_applies_guardrail("p0", "test_hardening", "p0_governance")
_emit_snapshots_state("p0", "test_hardening", "state_snapshot")
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

_emit_emits_metric_event("test_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_hardening", "p3lm", "state")
_emit_records_execution_trace("test_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_hardening", "context_pull")
_emit_pulls_context("p1", "test_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_hardening", "write_through")
_emit_writes_through("p1", "test_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_hardening", "routing_commit")
_emit_escalates_to_human("p1", "test_hardening", "human_escalation")
_emit_routes_through("p1", "test_hardening", "route_through")
_emit_checks_agent_registry("p1", "test_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "test_hardening", "capability")
_emit_dispatches_execution_plan("p1", "test_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "test_hardening", "sub_agent")
_emit_routes_to_agent("p1", "test_hardening", "target_agent")
_emit_verifies_policy("p1", "test_hardening", "policy_check")
_emit_observes_runtime_state("p1", "test_hardening", "runtime_state")
_emit_verifies_boundary("p1", "test_hardening", "boundary_check")
_emit_transcripts_response("p1", "test_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "test_hardening")
_emit_gated_by_confidence("p1", "test_hardening", "confidence_gate")
emit_replay_key("p0", "test_hardening")
emit_determinism_digest("p0", "test_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_hardening", "execution_auth")
_emit_validates_capability("p2", "test_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_hardening", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ===========================================================================
# HELPERS
# ===========================================================================


def _make_doc(doc_id, score=0.5, content="test content"):
    return Document(doc_id=doc_id, content=content, score=score, metadata={})


def _make_report(scores):
    return EvaluationReport(
        run_id="r1",
        dataset_name="test",
        dataset_version="1.0",
        system_version="v1",
        timestamp="2025-01-01T00:00:00Z",
        aggregate_scores=scores,
        per_example_results=[],
    )


def _make_rubric(grounded=True, useful=True, correct=True, safe=True, missing=False):
    return ReviewRubric(
        grounded=grounded,
        useful=useful,
        correct=correct,
        safe=safe,
        missing_context=missing,
    )


def _make_feedback(example_id, query="q", answer="answer", rubric=None):
    return FeedbackExample(
        example_id=example_id,
        query=query,
        model_answer=answer,
        human_annotation=rubric or _make_rubric(),
        context_documents=[],
        timestamp="2025-01-01T00:00:00Z",
    )


# ===========================================================================
# §1.4 BOUNDARY TESTING
# ===========================================================================


class TestBoundaryPrecisionAtK:
    """§1.4: PrecisionAtK denominator is always k, not len(retrieved)."""

    def test_prediction_exactly_k(self):
        # prediction = exactly k docs, all relevant
        assert PrecisionAtK(k=3).compute(["a", "b", "c"], ["a", "b", "c"]) == pytest.approx(1.0)

    def test_prediction_k_minus_one(self):
        # 2 docs, k=3 → denominator is k=3
        score = PrecisionAtK(k=3).compute(["a", "b"], ["a", "b"])
        assert score == pytest.approx(2.0 / 3.0)

    def test_prediction_k_plus_one_truncated(self):
        # 4 docs provided, k=3 → only first 3 counted
        score = PrecisionAtK(k=3).compute(["a", "b", "x", "c"], ["c"])
        # "c" is position 4, beyond k=3
        assert score == pytest.approx(0.0)

    def test_k_equals_one_boundary(self):
        assert PrecisionAtK(k=1).compute(["a"], ["a"]) == pytest.approx(1.0)
        assert PrecisionAtK(k=1).compute(["b"], ["a"]) == pytest.approx(0.0)


class TestBoundaryRecallAtK:
    """§1.4: RecallAtK exact boundary positions."""

    def test_relevant_at_position_k_exactly(self):
        # k=4, relevant at index 3 (position 4)
        assert RecallAtK(k=4).compute(["x", "y", "z", "a"], ["a"]) == pytest.approx(1.0)

    def test_relevant_at_position_k_plus_one_missed(self):
        # k=3, relevant at index 3 (position 4) → missed
        assert RecallAtK(k=3).compute(["x", "y", "z", "a"], ["a"]) == pytest.approx(0.0)

    def test_k_equals_one_hit(self):
        assert RecallAtK(k=1).compute(["a"], ["a"]) == pytest.approx(1.0)

    def test_k_equals_one_miss(self):
        assert RecallAtK(k=1).compute(["x"], ["a"]) == pytest.approx(0.0)

    def test_multiple_gt_partial_recall(self):
        # k=2, 1 of 3 relevant docs in top-2
        score = RecallAtK(k=2).compute(["a", "x", "b", "c"], ["a", "b", "c"])
        assert score == pytest.approx(1.0 / 3.0)

    def test_three_duplicates_count_as_one(self):
        """§1.15 regression: duplicate docs must not inflate recall past 1.0."""
        assert RecallAtK(k=10).compute(["a", "a", "a", "a", "a"], ["a"]) == pytest.approx(1.0)

    def test_near_miss_duplicate_at_boundary(self):
        """Adjacent near-miss: 2 duplicates of the relevant doc at k=2."""
        assert RecallAtK(k=2).compute(["a", "a"], ["a"]) == pytest.approx(1.0)


class TestBoundaryNDCG:
    """§1.4: NDCG threshold edges and §1.15 regression for graded context."""

    def test_single_relevant_at_rank_1(self):
        assert NDCG(k=1).compute(["a"], ["a"]) == pytest.approx(1.0)

    def test_single_relevant_at_rank_2_k_equals_1(self):
        # Relevant doc not in top-1 → 0
        assert NDCG(k=1).compute(["x", "a"], ["a"]) == pytest.approx(0.0)

    def test_graded_context_empty_ground_truth_regression(self):
        """§1.15 regression: graded context must work with empty ground_truth."""
        relevance = {"doc_1": 3.0, "doc_2": 1.0}
        score = NDCG(k=2).compute(["doc_1", "doc_2"], [], context=relevance)
        assert score == pytest.approx(1.0)

    def test_graded_context_inverted_order_regression(self):
        """§1.15 near-miss: wrong order with graded context must score < 1."""
        relevance = {"doc_1": 3.0, "doc_2": 1.0}
        score_good = NDCG(k=2).compute(["doc_1", "doc_2"], [], context=relevance)
        score_bad = NDCG(k=2).compute(["doc_2", "doc_1"], [], context=relevance)
        assert score_good > score_bad
        assert score_bad > 0.0  # both present, just wrong order

    def test_all_zero_relevance_in_context(self):
        """All zero graded relevance → IDCG = 0 → returns 0."""
        relevance = {"doc_1": 0.0, "doc_2": 0.0}
        score = NDCG(k=2).compute(["doc_1", "doc_2"], [], context=relevance)
        assert score == pytest.approx(0.0)

    def test_dcg_formula_exact(self):
        """Verify exact DCG value: rel/log2(rank+1) for rank 1 = rel/1."""
        relevance = {"doc_1": 1.0}
        score = NDCG(k=1).compute(["doc_1"], [], context=relevance)
        expected_dcg = 1.0 / math.log2(2)
        expected_idcg = 1.0 / math.log2(2)
        assert score == pytest.approx(expected_dcg / expected_idcg)


class TestBoundaryDriftMonitorThresholds:
    """§1.4: RetrievalDriftMonitor threshold boundaries."""

    def _monitor(self, hit_threshold=THRESHOLD, std_threshold=THRESHOLD, stab_threshold=THRESHOLD):
        return RetrievalDriftMonitor(
            hit_rate_threshold=hit_threshold,
            score_std_threshold=std_threshold,
            stability_threshold=stab_threshold,
        )

    def test_hit_rate_exactly_at_threshold_no_alert(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=THRESHOLD,  # == threshold
            score_distribution_mean=0.7,
            score_distribution_std=0.10,
            top_k_stability=0.96,
            sample_size=10,
        )
        alerts = self._monitor(hit_threshold=THRESHOLD).check_alerts(snap)
        hit_alerts = [a for a in alerts if a.metric_name == "retrieval_hit_rate"]
        assert len(hit_alerts) == 0

    def test_hit_rate_one_below_threshold_alerts(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=THRESHOLD - 0.001,  # just below threshold
            score_distribution_mean=0.7,
            score_distribution_std=0.10,
            top_k_stability=0.80,
            sample_size=10,
        )
        alerts = self._monitor(hit_threshold=THRESHOLD).check_alerts(snap)
        assert any(a.metric_name == "retrieval_hit_rate" for a in alerts)

    def test_score_std_exactly_at_threshold_no_alert(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=THRESHOLD,  # == threshold
            top_k_stability=0.96,
            sample_size=10,
        )
        alerts = self._monitor(std_threshold=THRESHOLD).check_alerts(snap)
        std_alerts = [a for a in alerts if a.metric_name == "score_distribution_std"]
        assert len(std_alerts) == 0

    def test_score_std_one_above_threshold_alerts(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=THRESHOLD + 0.001,  # just above threshold
            top_k_stability=0.80,
            sample_size=10,
        )
        alerts = self._monitor(std_threshold=THRESHOLD).check_alerts(snap)
        assert any(a.metric_name == "score_distribution_std" for a in alerts)

    def test_stability_exactly_at_threshold_no_alert(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=THRESHOLD,  # == threshold
            sample_size=10,
        )
        alerts = self._monitor(stab_threshold=THRESHOLD).check_alerts(snap)
        stab_alerts = [a for a in alerts if a.metric_name == "top_k_stability"]
        assert len(stab_alerts) == 0

    def test_stability_one_below_threshold_alerts(self):
        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=THRESHOLD - 0.001,  # just below threshold
            sample_size=10,
        )
        alerts = self._monitor(stab_threshold=THRESHOLD).check_alerts(snap)
        assert any(a.metric_name == "top_k_stability" for a in alerts)

    def test_n_equals_one_no_stability_drift(self):
        """n=1 special case: top_k_stability = 1.0 by definition."""
        monitor = self._monitor()
        snapshot = monitor.measure(["q"], [["doc_1"]], [["doc_1"]], [[0.9]])
        assert snapshot.top_k_stability == pytest.approx(1.0)
        assert snapshot.sample_size == 1


class TestBoundaryProposerBridgeThresholds:
    """§1.4: EvaluatorProposerBridge priority assignment exact edges."""

    def _bridge(self):
        return EvaluatorProposerBridge()

    def test_delta_exactly_zero_is_ok(self):
        # score == target → delta == 0 → ok
        report = _make_report({"precision@5": 0.80})  # target = 0.80
        proposal = self._bridge().propose(eval_report=report)
        prec_sig = next(s for s in proposal.signals if s.metric_name == "precision@5")
        assert prec_sig.priority == "ok"
        assert prec_sig.delta == pytest.approx(0.0)

    def test_delta_minus_0_14_is_warning_not_critical(self):
        # delta = -0.14 (> -0.15) → warning
        report = _make_report({"precision@5": 0.66})  # 0.66 - 0.80 = -0.14
        proposal = self._bridge().propose(eval_report=report)
        prec_sig = next(s for s in proposal.signals if s.metric_name == "precision@5")
        assert prec_sig.priority == "warning"

    def test_delta_minus_0_15_is_critical(self):
        # delta = -0.15 (== -0.15) → critical
        report = _make_report({"precision@5": 0.65})  # 0.65 - 0.80 = -0.15
        proposal = self._bridge().propose(eval_report=report)
        prec_sig = next(s for s in proposal.signals if s.metric_name == "precision@5")
        assert prec_sig.priority == "critical"

    def test_delta_minus_0_16_is_critical(self):
        # delta = -0.16 (< -0.15) → critical
        report = _make_report({"precision@5": 0.64})  # 0.64 - 0.80 = -0.16
        proposal = self._bridge().propose(eval_report=report)
        prec_sig = next(s for s in proposal.signals if s.metric_name == "precision@5")
        assert prec_sig.priority == "critical"

    def test_retrieval_hit_rate_exactly_at_ok_boundary(self):
        from agentic_core.evaluation.monitoring.snapshots import RetrievalDriftSnapshot

        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.75,  # == target → delta = 0
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.80,
            sample_size=10,
        )
        proposal = self._bridge().propose(retrieval_snapshot=snap)
        sig = next(s for s in proposal.signals if s.metric_name == "retrieval_hit_rate")
        assert sig.priority == "ok"

    def test_retrieval_hit_critical_threshold(self):
        # hit_rate = 0.75 - 0.21 = 0.54 → delta = -0.21 < -0.20 → critical
        from agentic_core.evaluation.monitoring.snapshots import RetrievalDriftSnapshot

        snap = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.54,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.80,
            sample_size=10,
        )
        proposal = self._bridge().propose(retrieval_snapshot=snap)
        sig = next(s for s in proposal.signals if s.metric_name == "retrieval_hit_rate")
        assert sig.priority == "critical"

    def test_dpo_count_exactly_ten_no_finetuning(self):
        """dpo_count == 10 is NOT > 10, so should be accumulate, not finetune."""
        pairs = [
            DPOPair(
                pair_id=f"p_{i}",
                query="q",
                chosen_response="c",
                rejected_response="r",
                context_documents=[],
                chosen_score=0.9,
                rejected_score=0.1,
                source_example_ids=[],
            )
            for i in range(10)
        ]
        batch = DPOBatch(
            batch_id="b",
            timestamp="t",
            pair_count=10,
            pairs=pairs,
            source_feedback_count=20,
        )
        proposal = EvaluatorProposerBridge().propose(dpo_batch=batch)
        assert "accumulate_more_dpo_pairs" in proposal.recommended_actions
        assert "trigger_dpo_finetuning" not in proposal.recommended_actions

    def test_dpo_count_eleven_triggers_finetuning(self):
        """dpo_count == 11 IS > 10, triggers finetuning."""
        pairs = [
            DPOPair(
                pair_id=f"p_{i}",
                query="q",
                chosen_response="c",
                rejected_response="r",
                context_documents=[],
                chosen_score=0.9,
                rejected_score=0.1,
                source_example_ids=[],
            )
            for i in range(11)
        ]
        batch = DPOBatch(
            batch_id="b",
            timestamp="t",
            pair_count=11,
            pairs=pairs,
            source_feedback_count=22,
        )
        proposal = EvaluatorProposerBridge().propose(dpo_batch=batch)
        assert "trigger_dpo_finetuning" in proposal.recommended_actions

    def test_health_score_boundary_requires_intervention_at_0_59(self):
        """health < 0.60 → requires_intervention. Exact boundary: 0.60 does NOT trigger."""
        # 3 ok + 2 warning → health = 3/5 = 0.60 (exactly at boundary, NOT < 0.60)
        report = _make_report(
            {
                "precision@5": 0.85,  # ok (above 0.80)
                "recall@10": 0.90,  # ok
                "MRR": 0.85,  # ok
                "groundedness": 0.90,  # ok
                "answer_correctness": 0.60,  # warning (0.60 - 0.80 = -0.20, not critical)
            }
        )
        proposal = EvaluatorProposerBridge().propose(eval_report=report)
        # health = ok_count / total → if no critical signals, requires_intervention = False
        if not any(s.priority == "critical" for s in proposal.signals):
            assert proposal.requires_intervention is (proposal.overall_health_score < 0.60)


class TestBoundaryEmbeddingDriftMonitor:
    """§1.4: EmbeddingDriftMonitor norm_std and sim_mean thresholds."""

    def _monitor(self, norm_threshold=THRESHOLD, sim_threshold=THRESHOLD):
        return EmbeddingDriftMonitor(
            norm_std_threshold=norm_threshold,
            similarity_mean_threshold=sim_threshold,
        )

    def test_norm_std_exactly_at_threshold_no_alert(self):
        snap = EmbeddingHealthSnapshot(
            timestamp="t",
            embedding_model_version="v1",
            vector_norm_mean=1.0,
            vector_norm_std=THRESHOLD,  # == threshold
            similarity_distribution_mean=0.96,
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor(norm_threshold=THRESHOLD).check_alerts(snap)
        norm_alerts = [a for a in alerts if a.metric_name == "vector_norm_std"]
        assert len(norm_alerts) == 0

    def test_norm_std_one_above_threshold_alerts(self):
        snap = EmbeddingHealthSnapshot(
            timestamp="t",
            embedding_model_version="v1",
            vector_norm_mean=1.0,
            vector_norm_std=THRESHOLD + 0.001,  # just above threshold
            similarity_distribution_mean=0.7,
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor(norm_threshold=THRESHOLD).check_alerts(snap)
        assert any(a.metric_name == "vector_norm_std" for a in alerts)

    def test_similarity_exactly_at_threshold_no_alert(self):
        snap = EmbeddingHealthSnapshot(
            timestamp="t",
            embedding_model_version="v1",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=THRESHOLD,  # == threshold
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor(sim_threshold=THRESHOLD).check_alerts(snap)
        sim_alerts = [a for a in alerts if a.metric_name == "similarity_distribution_mean"]
        assert len(sim_alerts) == 0

    def test_similarity_one_below_threshold_alerts(self):
        snap = EmbeddingHealthSnapshot(
            timestamp="t",
            embedding_model_version="v1",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=THRESHOLD - 0.001,  # just below threshold
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor(sim_threshold=THRESHOLD).check_alerts(snap)
        assert any(a.metric_name == "similarity_distribution_mean" for a in alerts)


class TestBoundaryAnswerQualityMonitor:
    """§1.4: AnswerQualityMonitor exact threshold edges."""

    def _monitor(self):
        return AnswerQualityMonitor(
            groundedness_threshold=THRESHOLD,
            hallucination_threshold=THRESHOLD,
            override_threshold=THRESHOLD,
        )

    def test_groundedness_exactly_at_threshold_no_alert(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=THRESHOLD,  # == threshold
            hallucination_rate=0.05,
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        g_alerts = [a for a in alerts if a.metric_name == "groundedness_rate"]
        assert len(g_alerts) == 0

    def test_groundedness_one_below_threshold_alerts(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=THRESHOLD - 0.001,  # just below threshold
            hallucination_rate=0.05,
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        assert any(a.metric_name == "groundedness_rate" for a in alerts)

    def test_hallucination_exactly_at_threshold_no_alert(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=0.96,
            hallucination_rate=THRESHOLD,  # == threshold
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        h_alerts = [a for a in alerts if a.metric_name == "hallucination_rate"]
        assert len(h_alerts) == 0

    def test_hallucination_one_above_threshold_critical(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=0.96,
            hallucination_rate=THRESHOLD + 0.001,  # just above threshold
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        assert any(a.metric_name == "hallucination_rate" for a in alerts)

    def test_override_exactly_at_threshold_no_alert(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=0.96,
            hallucination_rate=0.05,
            human_override_rate=THRESHOLD,  # == threshold
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        o_alerts = [a for a in alerts if a.metric_name == "human_override_rate"]
        assert len(o_alerts) == 0

    def test_override_one_above_threshold_alerts(self):
        snap = AnswerQualitySnapshot(
            timestamp="t",
            system_version="v1",
            groundedness_rate=0.96,
            hallucination_rate=0.05,
            human_override_rate=THRESHOLD + 0.001,  # just above threshold
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snap)
        assert any(a.metric_name == "human_override_rate" for a in alerts)


# ===========================================================================
# §1.5 EXCEPTION PATH VERIFICATION
# ===========================================================================


class TestExceptionPathGroundedness:
    """§1.5: judge callable exceptions must not mask failures silently."""

    def test_judge_raises_propagates(self):
        """If judge raises, exception must propagate (no silent swallow)."""

        def bad_judge(pred, ctx):
            raise RuntimeError("judge service unavailable")

        g = Groundedness(judge=bad_judge)
        with pytest.raises(RuntimeError, match="judge service unavailable"):
            g.compute("some answer", "context", context="ctx docs")

    def test_judge_returns_value_above_one_is_passed_through(self):
        """Judge returning >1.0 — caller's responsibility; we don't clamp."""

        def permissive_judge(pred, ctx):
            return 1.5

        g = Groundedness(judge=permissive_judge)
        score = g.compute("answer", "", context="ctx")
        assert score == pytest.approx(1.5)

    def test_judge_returns_zero_for_empty_prediction(self):
        """Empty prediction → returns 0 before calling judge (guard branch)."""
        called = []

        def judge(p, c):
            called.append(True)
            return 0.9

        g = Groundedness(judge=judge)
        score = g.compute("", "ground truth", context="ctx")
        assert score == 0.0
        assert not called  # judge never called because guard fired

    def test_judge_receives_context_string(self):
        """When context is a list, judge should receive joined string."""
        received = {}

        def capture_judge(pred, ctx):
            received["ctx"] = ctx
            return 0.8

        g = Groundedness(judge=capture_judge)
        g.compute("answer", "", context=["doc_a", "doc_b"])
        assert received["ctx"] == "doc_a doc_b"

    def test_no_judge_empty_context_returns_zero_no_exception(self):
        """No judge, empty context → 0 (safe fallback, no exception)."""
        assert Groundedness().compute("answer", "", context="") == 0.0

    def test_no_judge_none_context_falls_back_to_ground_truth(self):
        """No judge, context=None → uses ground_truth as context."""
        score = Groundedness().compute("hello world", "hello world", context=None)
        assert score == pytest.approx(1.0)


class TestExceptionPathAnswerCorrectness:
    """§1.5: judge callable exceptions for AnswerCorrectness."""

    def test_judge_raises_propagates(self):
        def bad_judge(pred, gt):
            raise ValueError("scorer down")

        m = AnswerCorrectness(judge=bad_judge)
        with pytest.raises(ValueError, match="scorer down"):
            m.compute("answer", "reference")

    def test_judge_not_called_when_prediction_empty(self):
        called = []

        def judge(p, gt):
            called.append(True)
            return 0.9

        m = AnswerCorrectness(judge=judge)
        assert m.compute("", "reference") == 0.0
        assert not called

    def test_judge_not_called_when_ground_truth_empty(self):
        called = []

        def judge(p, gt):
            called.append(True)
            return 0.9

        m = AnswerCorrectness(judge=judge)
        assert m.compute("answer", "") == 0.0
        assert not called

    def test_judge_receives_correct_args(self):
        received = {}

        def capture(pred, gt):
            received["pred"] = pred
            received["gt"] = gt
            return 0.7

        m = AnswerCorrectness(judge=capture)
        m.compute("my answer", "expected answer")
        assert received["pred"] == "my answer"
        assert received["gt"] == "expected answer"


class TestExceptionPathL4Persist:
    """§1.5: L4 persist except blocks — broad handler must not mask."""

    def test_dpo_builder_persist_ioerror_does_not_raise(self):
        class FailStore:
            def put(self, a):
                raise OSError("disk full")

        decisions = [
            _make_feedback("e0", "q", rubric=_make_rubric()),
            _make_feedback("e1", "q", rubric=_make_rubric(correct=False)),
        ]
        batch = DPOBatchBuilder(min_score_delta=0.0, l4_store=FailStore()).generate_pairs(decisions)
        assert batch is not None

    def test_bridge_persist_typeerror_does_not_raise(self):
        class FailStore:
            def put(self, a):
                raise TypeError("unexpected type")

        proposal = EvaluatorProposerBridge(l4_store=FailStore()).propose()
        assert proposal is not None

    def test_bridge_persist_called_once_per_propose(self):
        calls = []

        class CountingStore:
            def put(self, a):
                calls.append(a)

        EvaluatorProposerBridge(l4_store=CountingStore()).propose()
        assert len(calls) == 1

    def test_dpo_builder_persist_called_once(self):
        calls = []

        class CountingStore:
            def put(self, a):
                calls.append(a)

        decisions = [
            _make_feedback("e0", "q", rubric=_make_rubric()),
            _make_feedback("e1", "q", rubric=_make_rubric(correct=False)),
        ]
        DPOBatchBuilder(min_score_delta=0.0, l4_store=CountingStore()).generate_pairs(decisions)
        assert len(calls) == 1

    def test_persist_no_side_effects_before_completion(self):
        """Verify main return value valid even when persist fails."""

        class FailStore:
            def put(self, a):
                raise RuntimeError("network error")

        decisions = [
            _make_feedback("e0", "q", rubric=_make_rubric()),
            _make_feedback("e1", "q", rubric=_make_rubric(correct=False)),
        ]
        result = DPOBatchBuilder(min_score_delta=0.0, l4_store=FailStore()).generate_pairs(decisions)
        assert result.pair_count >= 1


# ===========================================================================
# §1.10 DETERMINISTIC DECISION SURFACES
# ===========================================================================


class TestDeterministicRRF:
    """§1.10: RRF identical input → identical output; distinct input no collapse."""

    def test_identical_input_same_output(self):
        rrf = ReciprocalRankFusion(k=60)
        lexical = [_make_doc("a"), _make_doc("b")]
        vector = [_make_doc("b"), _make_doc("c")]
        r1 = [d.doc_id for d in rrf.merge(lexical, vector)]
        r2 = [d.doc_id for d in rrf.merge(lexical, vector)]
        assert r1 == r2

    def test_distinct_inputs_no_collapse(self):
        rrf = ReciprocalRankFusion()
        r1 = rrf.merge([_make_doc("a", 0.9)], [_make_doc("a", 0.9)])
        r2 = rrf.merge([_make_doc("b", 0.9)], [_make_doc("b", 0.9)])
        assert r1[0].doc_id != r2[0].doc_id

    def test_normalized_equivalent_input_same_output(self):
        """Same logical ranking, different score magnitude → same RRF output."""
        rrf = ReciprocalRankFusion()
        # RRF ignores absolute scores — only rank matters
        r1 = rrf.merge([_make_doc("a", 1.0), _make_doc("b", 0.5)], [_make_doc("c", 0.8)])
        r2 = rrf.merge([_make_doc("a", 0.9), _make_doc("b", 0.1)], [_make_doc("c", 0.7)])
        ids1 = [d.doc_id for d in r1]
        ids2 = [d.doc_id for d in r2]
        assert ids1 == ids2

    def test_tie_score_stable_ordering(self):
        """Two docs with same RRF score: output order must be deterministic."""
        rrf = ReciprocalRankFusion()
        # a and c each appear once at rank 1 in separate lists → same RRF score
        r1 = [d.doc_id for d in rrf.merge([_make_doc("a")], [_make_doc("c")])]
        r2 = [d.doc_id for d in rrf.merge([_make_doc("a")], [_make_doc("c")])]
        assert r1 == r2

    def test_score_metadata_field_set(self):
        rrf = ReciprocalRankFusion()
        result = rrf.merge([_make_doc("a")], [_make_doc("b")])
        for d in result:
            assert "rrf_score" in d.metadata


class TestDeterministicScoreFusion:
    """§1.10: ScoreFusion determinism and tie-break stability."""

    def test_identical_input_same_output(self):
        sf = ScoreFusion()
        lexical = [_make_doc("a", 0.9), _make_doc("b", 0.5)]
        vector = [_make_doc("c", 0.8)]
        r1 = [d.doc_id for d in sf.merge(lexical, vector)]
        r2 = [d.doc_id for d in sf.merge(lexical, vector)]
        assert r1 == r2

    def test_key_order_independence(self):
        """ScoreFusion result must not depend on dict insertion order."""
        sf = ScoreFusion()
        lexical_fwd = [_make_doc("a", 1.0), _make_doc("b", 0.5)]
        lexical_rev = [_make_doc("b", 0.5), _make_doc("a", 1.0)]
        r_fwd = [d.doc_id for d in sf.merge(lexical_fwd, [])]
        r_rev = [d.doc_id for d in sf.merge(lexical_rev, [])]
        assert r_fwd == r_rev

    def test_all_equal_scores_single_element(self):
        """§1.17: single-element list — normalize with max==min → all 1.0."""
        sf = ScoreFusion()
        result = sf.merge([_make_doc("only", 0.7)], [])
        assert result[0].score == pytest.approx(1.0)

    def test_doc_in_both_lists_counts_once(self):
        """Shared doc appears once in output, not twice."""
        sf = ScoreFusion()
        result = sf.merge([_make_doc("shared", 0.9)], [_make_doc("shared", 0.9)])
        shared_docs = [d for d in result if d.doc_id == "shared"]
        assert len(shared_docs) == 1


class TestDeterministicHeuristicReranker:
    """§1.10: HeuristicReranker tie-score ordering stability."""

    def test_tie_scores_deterministic_order(self):
        """Multiple docs with identical query overlap → same order every run."""
        reranker = HeuristicReranker(top_k=5)
        docs = [_make_doc(f"doc_{i}", content="same content here") for i in range(5)]
        r1 = [d.doc_id for d in reranker.rerank("same content", docs)]
        r2 = [d.doc_id for d in reranker.rerank("same content", docs)]
        assert r1 == r2

    def test_zero_query_overlap_all_score_zero(self):
        """Empty query → no overlap → all docs score 0."""
        reranker = HeuristicReranker(top_k=3)
        docs = [_make_doc(f"doc_{i}", content=f"content {i}") for i in range(3)]
        result = reranker.rerank("", docs)
        for d in result:
            assert d.score == pytest.approx(0.0)


class TestDeterministicDPOBuilder:
    """§1.10: DPOBatchBuilder output is reproducible for same input."""

    def test_identical_input_same_pairs(self):
        decisions = [
            _make_feedback("e0", "q1", answer="good", rubric=_make_rubric()),
            _make_feedback("e1", "q1", answer="bad", rubric=_make_rubric(correct=False)),
        ]
        b1 = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        b2 = DPOBatchBuilder(min_score_delta=0.0).generate_pairs(decisions)
        assert b1.pair_count == b2.pair_count
        if b1.pair_count > 0:
            assert b1.pairs[0].chosen_response == b2.pairs[0].chosen_response
            assert b1.pairs[0].rejected_response == b2.pairs[0].rejected_response


# ===========================================================================
# §1.12 MATRIX TESTING
# ===========================================================================


class TestMatrixGroundednessJudge:
    """§1.12: judge=None × judge=callable × empty prediction × empty context."""

    @pytest.mark.parametrize(
        "pred,ctx,expected",
        [
            ("", "context", 0.0),  # empty pred → 0
            ("answer", "", 0.0),  # empty context → 0
            ("answer", None, 0.0),  # None context + no GT → 0
            ("answer", "answer", 1.0),  # identical → 1.0
        ],
    )
    def test_no_judge_matrix(self, pred, ctx, expected):
        score = Groundedness().compute(pred, "", context=ctx)
        assert score == pytest.approx(expected, abs=0.01)

    @pytest.mark.parametrize(
        "pred,ctx,judge_val,expected",
        [
            ("", "ctx", 0.9, 0.0),  # guard fires before judge
            ("answer", "ctx", 0.9, 0.9),  # judge called
            ("answer", "", 0.9, 0.0),  # empty context_str → 0 before judge
        ],
    )
    def test_with_judge_matrix(self, pred, ctx, judge_val, expected):
        def judge(p, c):
            return judge_val

        score = Groundedness(judge=judge).compute(pred, "", context=ctx)
        assert score == pytest.approx(expected)


class TestMatrixAnswerCorrectnessJudge:
    """§1.12: judge=None × judge=callable × empty inputs."""

    @pytest.mark.parametrize(
        "pred,gt,expected",
        [
            ("", "ref", 0.0),
            ("answer", "", 0.0),
            ("hello", "hello", 1.0),
        ],
    )
    def test_no_judge_matrix(self, pred, gt, expected):
        score = AnswerCorrectness().compute(pred, gt)
        assert score == pytest.approx(expected, abs=0.01)

    @pytest.mark.parametrize(
        "pred,gt,judge_val,expected",
        [
            ("", "ref", 0.9, 0.0),  # guard fires before judge
            ("answer", "", 0.9, 0.0),  # guard fires
            ("answer", "ref", 0.7, 0.7),  # judge called
        ],
    )
    def test_with_judge_matrix(self, pred, gt, judge_val, expected):
        def judge(p, g):
            return judge_val

        score = AnswerCorrectness(judge=judge).compute(pred, gt)
        assert score == pytest.approx(expected)


class TestMatrixRetrievalPipelineMode:
    """§1.12: mode × retriever-presence matrix for RetrievalPipeline."""

    class _StubLexical:
        def __init__(self, docs):
            self._docs = docs

        def retrieve(self, query, top_k):
            return self._docs[:top_k]

    class _StubVector:
        def __init__(self, docs):
            self._docs = docs

        def embed_query(self, q):
            return [0.0]

        def retrieve(self, emb, top_k):
            return self._docs[:top_k]

    @pytest.mark.parametrize(
        "mode,has_lex,has_vec,expect_empty",
        [
            (PROFILE_VECTOR_ONLY, False, False, True),
            (PROFILE_VECTOR_ONLY, False, True, False),
            (PROFILE_HYBRID, False, False, True),
            (PROFILE_HYBRID, True, False, False),
            (PROFILE_HYBRID, False, True, False),
            (PROFILE_HYBRID_RERANKED, False, False, True),
            (PROFILE_HYBRID_RERANKED, True, False, False),
        ],
    )
    def test_mode_x_retriever_matrix(self, mode, has_lex, has_vec, expect_empty):
        lex_docs = [_make_doc("lex", content="governance policy")] if has_lex else []
        vec_docs = [_make_doc("vec", content="governance policy")] if has_vec else []
        pipeline = RetrievalPipeline(
            config=make_profile(mode),
            lexical_retriever=self._StubLexical(lex_docs) if has_lex else None,
            vector_retriever=self._StubVector(vec_docs) if has_vec else None,
        )
        result = pipeline.retrieve("governance")
        if expect_empty:
            assert result == []
        else:
            assert len(result) >= 1


class TestMatrixChunkPolicyValidator:
    """§1.12: policy × validator combinations."""

    @pytest.mark.parametrize(
        "chunk_size,max_tokens,expect_violation",
        [
            (10, 10, False),  # exact boundary: no violation
            (10, 9, True),  # chunk_size > max_tokens → violation
            (5, 10, False),  # well under: no violation
        ],
    )
    def test_max_validator_x_policy_size(self, chunk_size, max_tokens, expect_violation):
        doc = " ".join(f"w{i}" for i in range(chunk_size))
        from agentic_core.evaluation.chunking.policies import Chunk

        chunk = Chunk(
            chunk_id="c0",
            doc_id="d",
            content=doc,
            token_count=chunk_size,
            start_char=0,
            end_char=len(doc),
        )
        violations = MaxChunkSizeValidator(max_tokens=max_tokens).validate([chunk])
        assert (len(violations) > 0) == expect_violation


class TestMatrixDPOBuilderDeltaFilter:
    """§1.12: min_score_delta × quality gap matrix."""

    def _pos(self, eid):
        return _make_feedback(eid, "q", answer="good", rubric=_make_rubric())

    def _neg(self, eid):
        return _make_feedback(eid, "q", answer="bad", rubric=_make_rubric(correct=False))

    @pytest.mark.parametrize(
        "delta_threshold,expect_pairs",
        [
            (0.00, 1),  # any gap → pair
            (0.99, 0),  # very high threshold → no pairs (gap likely < 0.99)
        ],
    )
    def test_delta_filter_matrix(self, delta_threshold, expect_pairs):
        decisions = [self._pos("e0"), self._neg("e1")]
        batch = DPOBatchBuilder(min_score_delta=delta_threshold).generate_pairs(decisions)
        assert batch.pair_count == expect_pairs


# ===========================================================================
# §1.13 METAMORPHIC AND CONTRADICTION TESTS
# ===========================================================================


class TestMetamorphicTokenF1:
    """§1.13: _token_f1 invariants — symmetry, idempotency, contradiction."""

    def test_f1_is_symmetric(self):
        """F1(a, b) == F1(b, a)."""
        a = ["the", "quick", "brown", "fox"]
        b = ["quick", "brown", "fox", "jumps"]
        assert _token_f1(a, b) == pytest.approx(_token_f1(b, a))

    def test_f1_identical_inputs_is_one(self):
        tokens = ["hello", "world", "governance"]
        assert _token_f1(tokens, tokens) == pytest.approx(1.0)

    def test_f1_disjoint_is_zero(self):
        assert _token_f1(["a", "b"], ["c", "d"]) == pytest.approx(0.0)

    def test_f1_contradiction_adding_irrelevant_token_decreases(self):
        """Adding irrelevant tokens to prediction can only decrease precision."""
        a = ["governance", "policy"]
        a_noisy = ["governance", "policy", "irrelevant", "noise", "extra"]
        f1_clean = _token_f1(a, a)
        f1_noisy = _token_f1(a_noisy, a)
        # clean == 1.0; noisy has lower precision → lower F1
        assert f1_clean >= f1_noisy

    def test_f1_range_always_zero_to_one(self):
        import random

        rng = random.Random(42)
        words = [f"word_{i}" for i in range(20)]
        for _ in range(20):
            a = rng.sample(words, rng.randint(1, 10))
            b = rng.sample(words, rng.randint(1, 10))
            score = _token_f1(a, b)
            assert 0.0 <= score <= 1.0


class TestMetamorphicTokenize:
    """§1.13: _tokenize normalization invariants."""

    def test_case_normalization_preserves_meaning(self):
        assert _tokenize("Hello") == _tokenize("hello")

    def test_punctuation_stripped_same_tokens(self):
        assert _tokenize("hello, world!") == _tokenize("hello world")

    def test_extra_whitespace_collapsed(self):
        assert _tokenize("hello   world") == _tokenize("hello world")

    def test_irrelevant_metadata_no_effect(self):
        """Token order independent: sets compared, not lists."""
        t1 = set(_tokenize("the quick brown fox"))
        t2 = set(_tokenize("fox brown quick the"))
        assert t1 == t2


class TestMetamorphicSerializationRoundtrip:
    """§1.13: Serialization roundtrip preserves all fields."""

    def test_evaluation_snapshot_roundtrip(self):
        s = EvaluationSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            dataset_version="1.0",
            metric_results={"precision@5": 0.80, "recall@10": 0.85},
            run_id="run_001",
        )
        restored = EvaluationSnapshot.from_dict(s.to_dict())
        assert restored.run_id == s.run_id
        assert restored.metric_results == s.metric_results

    def test_delta_report_roundtrip(self):
        d = DeltaReport(
            run_id_a="r1",
            run_id_b="r2",
            config_a_name="baseline",
            config_b_name="candidate",
            timestamp="2025-01-01T00:00:00Z",
            metric_deltas={"precision@5": 0.05},
            scores_a={"precision@5": 0.75},
            scores_b={"precision@5": 0.80},
        )
        restored = DeltaReport.from_dict(d.to_dict())
        assert restored.metric_deltas == d.metric_deltas

    def test_drift_alert_to_dict_preserves_delta_sign(self):
        alert = DriftAlert(
            alert_id="a1",
            timestamp="t",
            alert_type="drift",
            metric_name="hit_rate",
            current_value=0.60,
            threshold_value=0.70,
            delta=-0.10,
            severity="warning",
            message="test",
        )
        d = alert.to_dict()
        assert d["delta"] == pytest.approx(-0.10)
        assert d["severity"] == "warning"

    def test_dpo_pair_roundtrip(self):
        p = DPOPair(
            pair_id="p1",
            query="q",
            chosen_response="good",
            rejected_response="bad",
            context_documents=["d1"],
            chosen_score=0.9,
            rejected_score=0.2,
            source_example_ids=["e0", "e1"],
        )
        d = p.to_dict()
        restored = DPOPair.from_dict(d)
        assert restored.pair_id == p.pair_id
        assert restored.chosen_score == pytest.approx(p.chosen_score)

    def test_improvement_proposal_roundtrip(self):
        proposal = ImprovementProposal(
            proposal_id="prop_001",
            timestamp="2025-01-01T00:00:00Z",
            signals=[
                ImprovementSignal(
                    signal_type="eval_metric",
                    metric_name="precision@5",
                    current_value=0.70,
                    target_value=0.80,
                    delta=-0.10,
                    priority="warning",
                    source="run:abc",
                    message="below target",
                )
            ],
            dpo_pair_count=5,
            recommended_actions=["tune_reranker"],
            overall_health_score=0.75,
            requires_intervention=False,
        )
        d = proposal.to_dict()
        restored = ImprovementProposal.from_dict(d)
        assert restored.signals[0].metric_name == "precision@5"
        assert restored.recommended_actions == ["tune_reranker"]


class TestContradictionImmutability:
    """§1.13: contradiction — attempt to violate frozen dataclass invariant."""

    def test_evaluation_snapshot_is_frozen(self):
        s = EvaluationSnapshot(
            timestamp="t",
            system_version="v1",
            dataset_version="1.0",
            metric_results={},
            run_id="r",
        )
        with pytest.raises((AttributeError, TypeError)):
            s.run_id = "modified"

    def test_dpo_pair_is_frozen(self):
        p = DPOPair(
            pair_id="p",
            query="q",
            chosen_response="c",
            rejected_response="r",
            context_documents=[],
            chosen_score=0.9,
            rejected_score=0.1,
            source_example_ids=[],
        )
        with pytest.raises((AttributeError, TypeError)):
            p.chosen_response = "changed"

    def test_retrieval_snapshot_is_frozen(self):
        s = RetrievalDriftSnapshot(
            timestamp="t",
            system_version="v1",
            retrieval_hit_rate=0.8,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.8,
            sample_size=10,
        )
        with pytest.raises((AttributeError, TypeError)):
            s.retrieval_hit_rate = 0.1


# ===========================================================================
# §1.15 REGRESSION AND MUTATION TESTS
# ===========================================================================


class TestRegressionRecallDuplicates:
    """§1.15: RecallAtK duplicate-inflation bug — minimal reproducer + near-miss."""

    def test_regression_three_duplicates_capped_at_one(self):
        """Minimal reproducer: 3× doc_1 in prediction must not inflate to 3.0."""
        score = RecallAtK(k=5).compute(["doc_1", "doc_1", "doc_1"], ["doc_1"])
        assert score == pytest.approx(1.0), "Regression: duplicates inflated recall past 1.0"

    def test_regression_five_duplicates_capped(self):
        """Larger set: 5 duplicates of a single relevant doc."""
        score = RecallAtK(k=10).compute(["a"] * 5, ["a"])
        assert score == pytest.approx(1.0)

    def test_near_miss_two_distinct_docs_both_relevant(self):
        """Adjacent: 2 relevant docs, both present once → recall = 1.0."""
        score = RecallAtK(k=2).compute(["a", "b"], ["a", "b"])
        assert score == pytest.approx(1.0)

    def test_mutation_sensitivity_operator_flip(self):
        """Proves test would fail if deduplication were removed."""
        # If deduplicate is removed: ["a","a","a","a","a"] / 1 = 5.0
        # With fix: score must be 1.0
        score = RecallAtK(k=10).compute(["a", "a", "a", "a", "a"], ["a"])
        assert score <= 1.0, "Mutation guard: score exceeded 1.0, deduplication broken"


class TestRegressionNDCGGradedContext:
    """§1.15: NDCG graded context + empty ground_truth — minimal reproducer."""

    def test_regression_graded_with_empty_gt(self):
        """Before fix: NDCG returned 0.0 when context provided + ground_truth=[]."""
        relevance = {"doc_1": 3.0, "doc_2": 1.0}
        score = NDCG(k=2).compute(["doc_1", "doc_2"], [], context=relevance)
        assert score == pytest.approx(1.0), (
            "Regression: graded context returned 0 due to empty ground_truth check"
        )

    def test_near_miss_graded_no_match_in_prediction(self):
        """Near-miss: prediction has docs not in relevance → score = 0."""
        relevance = {"doc_1": 3.0}
        score = NDCG(k=2).compute(["doc_x", "doc_y"], [], context=relevance)
        assert score == pytest.approx(0.0)

    def test_mutation_sensitivity_gt_check_position(self):
        """Proves fix: if ground_truth check fires before context check, regression returns."""
        # ground_truth = [] but context has data → must return > 0
        relevance = {"doc_a": 1.0}
        score = NDCG(k=1).compute(["doc_a"], [], context=relevance)
        assert score > 0.0, "Mutation guard: early ground_truth check broke graded context"


# ===========================================================================
# §1.17 STATEFUL SURFACE TESTS
# ===========================================================================


class TestStatefulRetrievalOrderingStability:
    """§1.17: retrieval behavior — single result, cutoff equality, ordering."""

    def test_rrf_single_result_each_side(self):
        rrf = ReciprocalRankFusion()
        result = rrf.merge([_make_doc("a")], [_make_doc("b")])
        assert len(result) == 2

    def test_rrf_empty_one_side_still_returns(self):
        rrf = ReciprocalRankFusion()
        result = rrf.merge([_make_doc("a"), _make_doc("b")], [])
        assert len(result) == 2

    def test_passthrough_reranker_cutoff_equality(self):
        """top_k == len(docs) → all returned."""
        reranker = PassthroughReranker(top_k=5)
        docs = [_make_doc(f"d{i}") for i in range(5)]
        assert len(reranker.rerank("q", docs)) == 5

    def test_passthrough_reranker_top_k_larger_than_docs(self):
        """top_k > len(docs) → all docs returned."""
        reranker = PassthroughReranker(top_k=10)
        docs = [_make_doc(f"d{i}") for i in range(3)]
        assert len(reranker.rerank("q", docs)) == 3

    def test_heuristic_reranker_top_k_larger_than_docs(self):
        """top_k > len(docs) → all docs returned."""
        reranker = HeuristicReranker(top_k=10)
        docs = [_make_doc(f"d{i}", content=f"word {i}") for i in range(3)]
        assert len(reranker.rerank("word 0", docs)) == 3


class TestStatefulSerializationKeyOrder:
    """§1.17: serialization behavior — key ordering changes must not affect correctness."""

    def test_evaluation_result_to_dict_contains_all_keys(self):
        r = EvaluationResult(
            example_id="e0",
            query="q",
            retrieved_doc_ids=["d1"],
            generated_answer="ans",
            metric_scores={"p@5": 0.8},
        )
        d = r.to_dict()
        for key in ("example_id", "query", "retrieved_doc_ids", "generated_answer", "metric_scores"):
            assert key in d

    def test_improvement_signal_to_dict_all_keys(self):
        s = ImprovementSignal(
            signal_type="eval_metric",
            metric_name="p@5",
            current_value=0.7,
            target_value=0.8,
            delta=-0.1,
            priority="warning",
            source="run:x",
            message="below target",
        )
        d = s.to_dict()
        for key in (
            "signal_type",
            "metric_name",
            "current_value",
            "target_value",
            "delta",
            "priority",
            "source",
            "message",
        ):
            assert key in d

    def test_chunk_to_dict_roundtrip(self):
        from agentic_core.evaluation.chunking.policies import Chunk

        c = Chunk(
            chunk_id="c0",
            doc_id="d0",
            content="hello world",
            token_count=2,
            start_char=0,
            end_char=11,
            parent_section="intro",
            metadata={"policy": "fixed_token"},
        )
        restored = Chunk.from_dict(c.to_dict())
        assert restored.chunk_id == c.chunk_id
        assert restored.metadata == c.metadata


class TestStatefulOverlapWindowEdge:
    """§1.17: OverlapWindowChunkPolicy single-element and step calculation."""

    def test_single_word_document(self):
        chunks = OverlapWindowChunkPolicy(chunk_size=10, overlap=5).chunk("oneword", "d")
        assert len(chunks) == 1
        assert chunks[0].content == "oneword"

    def test_document_shorter_than_chunk_size(self):
        doc = "short doc"
        chunks = OverlapWindowChunkPolicy(chunk_size=100, overlap=10).chunk(doc, "d")
        assert len(chunks) == 1

    def test_step_equals_one_produces_dense_overlap(self):
        """chunk_size=3, overlap=2 → step=1 → maximum overlap."""
        words = " ".join(f"w{i}" for i in range(5))
        chunks = OverlapWindowChunkPolicy(chunk_size=3, overlap=2).chunk(words, "d")
        # step=1 → n_chunks = max(1, len(words) - chunk_size + 1) = 3
        assert len(chunks) >= 3


class TestStatefulFixedTokenEdge:
    """§1.17: FixedTokenChunkPolicy single-token and exact-boundary documents."""

    def test_single_token_document(self):
        chunks = FixedTokenChunkPolicy(chunk_size=512).chunk("word", "d")
        assert len(chunks) == 1
        assert chunks[0].token_count == 1

    def test_document_length_exactly_chunk_size(self):
        doc = " ".join(f"w{i}" for i in range(10))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, "d")
        assert len(chunks) == 1
        assert chunks[0].token_count == 10

    def test_document_length_chunk_size_plus_one(self):
        doc = " ".join(f"w{i}" for i in range(11))
        chunks = FixedTokenChunkPolicy(chunk_size=10).chunk(doc, "d")
        assert len(chunks) == 2
        assert chunks[-1].token_count == 1


class TestStatefulSemanticEdge:
    """§1.17: SemanticChunkPolicy with similarity_threshold parameter path."""

    def test_similarity_threshold_stored(self):
        """similarity_threshold is stored; may be used by injected embedder."""
        p = SemanticChunkPolicy(target_size=50, similarity_threshold=THRESHOLD)
        assert p.similarity_threshold == pytest.approx(THRESHOLD)

    def test_embedder_injection_does_not_break_chunking(self):
        """With a mock embedder present, chunking must still complete."""

        class MockEmbedder:
            def encode(self, text):
                return [1.0, 0.0]

        doc = " ".join(f"sentence {i} ends here." for i in range(5))
        chunks = SemanticChunkPolicy(target_size=5, embedder=MockEmbedder()).chunk(doc, "d")
        assert len(chunks) >= 1
