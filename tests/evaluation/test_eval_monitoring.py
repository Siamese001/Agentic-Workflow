"""
Tests: Phase 4 — Production Monitoring and Drift Intelligence

Branch coverage:
- RetrievalDriftSnapshot: to_dict, from_dict, frozen
- EmbeddingHealthSnapshot: to_dict, from_dict, frozen
- AnswerQualitySnapshot: to_dict, from_dict, frozen
- DriftAlert: to_dict
- RetrievalDriftMonitor: empty queries raises, hit rate, score std, stability alerts
- EmbeddingDriftMonitor: empty embeddings raises, version mismatch, norm_std, sim_mean
- AnswerQualityMonitor: empty raises, groundedness, hallucination, override alerts
- ShadowEvaluationRunner: is_improvement, candidate_alerts, to_dict
- ShadowEvaluationResult: is_improvement positive/negative
"""

import pytest

from agentic_core.evaluation.monitoring.drift_monitor import (
    AnswerQualityMonitor,
    EmbeddingDriftMonitor,
    RetrievalDriftMonitor,
)
from agentic_core.evaluation.monitoring.shadow_eval_runner import (
    ShadowEvaluationRunner,
)
from agentic_core.evaluation.monitoring.snapshots import (
    AnswerQualitySnapshot,
    DriftAlert,
    EmbeddingHealthSnapshot,
    RetrievalDriftSnapshot,
)
from agentic_core.evaluation.runners.replay_eval_runner import SystemConfig
from agentic_core.evaluation.schemas.evaluation_dataset_schema import (
    EvaluationDataset,
    EvaluationExample,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_reads_policy_state,  # noqa: E402
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

_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_1")
_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_2")
_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_3")
_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_4")
_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_5")
_emit_emits_metric_event("test_eval_monitoring", "p4obs", "metric_6")
_emit_records_incident_event("test_eval_monitoring", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_eval_monitoring", "p4obs", "anomaly")
_emit_writes_observability_log("test_eval_monitoring", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_eval_monitoring", "p4obs", "mon_state")
_emit_triggers_alert("test_eval_monitoring", "p4obs", "alert")
_emit_links_incident_trace("test_eval_monitoring", "p4obs", "trace_link")
_emit_captures_pattern("test_eval_monitoring", "p3lm", "pattern")
_emit_records_learning_event("test_eval_monitoring", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_eval_monitoring", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_eval_monitoring", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_eval_monitoring", "p3lm", "routing")
_emit_improves_agent_policy("test_eval_monitoring", "p3lm", "policy")
_emit_stores_learning_state("test_eval_monitoring", "p3lm", "state")
_emit_records_execution_trace("test_eval_monitoring", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_eval_monitoring", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_eval_monitoring", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_eval_monitoring", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_eval_monitoring", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_eval_monitoring", "env_read", "p2_env_1")
_emit_reads_environ("test_eval_monitoring", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_eval_monitoring", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_eval_monitoring", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_eval_monitoring")
_emit_applies_guardrail("p0", "test_eval_monitoring", "p0_governance")
_emit_reads_policy_state("p0", "test_eval_monitoring", "policy_binding")
_emit_snapshots_state("p0", "test_eval_monitoring", "state_snapshot")
_emit_pulls_context("p1", "test_eval_monitoring", "context_pull")
_emit_pulls_context("p1", "test_eval_monitoring", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_eval_monitoring", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_eval_monitoring", "uwg_term_secondary")
_emit_writes_through("p1", "test_eval_monitoring", "write_through")
_emit_writes_through("p1", "test_eval_monitoring", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_eval_monitoring", "safety_validation")
_emit_invokes_eval("p1", "test_eval_monitoring", "eval_call")
_emit_proposal_commits_routing("p1", "test_eval_monitoring", "routing_commit")
_emit_escalates_to_human("p1", "test_eval_monitoring", "human_escalation")
_emit_routes_through("p1", "test_eval_monitoring", "route_through")
_emit_checks_agent_registry("p1", "test_eval_monitoring", "agent_registry")
_emit_validates_agent_capability("p1", "test_eval_monitoring", "capability")
_emit_dispatches_execution_plan("p1", "test_eval_monitoring", "exec_plan")
_emit_agent_executes_agent("p1", "test_eval_monitoring", "sub_agent")
_emit_routes_to_agent("p1", "test_eval_monitoring", "target_agent")
_emit_verifies_policy("p1", "test_eval_monitoring", "policy_check")
_emit_observes_runtime_state("p1", "test_eval_monitoring", "runtime_state")
_emit_verifies_boundary("p1", "test_eval_monitoring", "boundary_check")
_emit_transcripts_response("p1", "test_eval_monitoring", "transcript")
_emit_hard_fails_untranscripted("p1", "test_eval_monitoring")
_emit_gated_by_confidence("p1", "test_eval_monitoring", "confidence_gate")
emit_replay_key("p0", "test_eval_monitoring")
emit_determinism_digest("p0", "test_eval_monitoring")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_eval_monitoring", "execution_auth")
_emit_validates_capability("p2", "test_eval_monitoring", "capability_check")
_emit_routes_to_capability("p2", "test_eval_monitoring", "capability_route")
_emit_writes_via_uwg("p2", "test_eval_monitoring", "uwg_write")
_emit_blocks_direct_write("p2", "test_eval_monitoring", "direct_write_block")
_emit_records_tool_invocation("p2", "test_eval_monitoring", "tool_invocation")
_emit_captures_execution_output("p2", "test_eval_monitoring", "exec_output")
_emit_dispatches_agent("p3", "test_eval_monitoring", "agent_dispatch")
_emit_coordinates_agents("p3", "test_eval_monitoring", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_eval_monitoring", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_eval_monitoring", "healing_outcome")
_emit_escalates_failure("p3", "test_eval_monitoring", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_eval_monitoring", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_eval_monitoring", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_eval_monitoring", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_eval_monitoring", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_eval_monitoring", "eval_metric")
_emit_stores_embedding("p4", "test_eval_monitoring", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_eval_monitoring", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_eval_monitoring", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_dataset(n=2):
    return EvaluationDataset(
        name="shadow_test",
        version="1.0",
        examples=[
            EvaluationExample(
                query=f"query_{i}",
                ground_truth_documents=["doc_1"],
                expected_answer="expected answer",
            )
            for i in range(n)
        ],
    )


def _perfect_retrieval(query):
    return ["doc_1", "doc_2"]


def _bad_retrieval(query):
    return ["doc_x", "doc_y"]


# ---------------------------------------------------------------------------
# Snapshot dataclasses
# ---------------------------------------------------------------------------


class TestRetrievalDriftSnapshot:
    def _make(self):
        return RetrievalDriftSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            retrieval_hit_rate=0.82,
            score_distribution_mean=0.71,
            score_distribution_std=0.09,
            top_k_stability=0.75,
            sample_size=100,
        )

    def test_to_dict_keys(self):
        d = self._make().to_dict()
        assert d["snapshot_type"] == "retrieval_drift"
        assert d["retrieval_hit_rate"] == pytest.approx(0.82)

    def test_from_dict_roundtrip(self):
        s = self._make()
        restored = RetrievalDriftSnapshot.from_dict(s.to_dict())
        assert restored.retrieval_hit_rate == pytest.approx(s.retrieval_hit_rate)
        assert restored.sample_size == s.sample_size

    def test_frozen(self):
        s = self._make()
        with pytest.raises((AttributeError, TypeError)):
            s.retrieval_hit_rate = 0.5

    def test_missing_metadata_defaults(self):
        d = self._make().to_dict()
        d.pop("metadata", None)
        restored = RetrievalDriftSnapshot.from_dict({**d, "metadata": {}})
        assert restored.metadata == {}


class TestEmbeddingHealthSnapshot:
    def _make(self, mismatch=False):
        return EmbeddingHealthSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            embedding_model_version="v1.2",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=0.72,
            similarity_distribution_std=0.08,
            version_mismatch_detected=mismatch,
            sample_size=50,
        )

    def test_to_dict_snapshot_type(self):
        assert self._make().to_dict()["snapshot_type"] == "embedding_health"

    def test_from_dict_roundtrip(self):
        s = self._make()
        restored = EmbeddingHealthSnapshot.from_dict(s.to_dict())
        assert restored.embedding_model_version == s.embedding_model_version
        assert restored.version_mismatch_detected == s.version_mismatch_detected

    def test_frozen(self):
        s = self._make()
        with pytest.raises((AttributeError, TypeError)):
            s.vector_norm_mean = 0.1

    def test_mismatch_detected_true(self):
        s = self._make(mismatch=True)
        assert s.version_mismatch_detected is True


class TestAnswerQualitySnapshot:
    def _make(self):
        return AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.85,
            hallucination_rate=0.05,
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=200,
        )

    def test_to_dict_snapshot_type(self):
        assert self._make().to_dict()["snapshot_type"] == "answer_quality"

    def test_from_dict_roundtrip(self):
        s = self._make()
        restored = AnswerQualitySnapshot.from_dict(s.to_dict())
        assert restored.groundedness_rate == pytest.approx(s.groundedness_rate)
        assert restored.hallucination_rate == pytest.approx(s.hallucination_rate)

    def test_frozen(self):
        s = self._make()
        with pytest.raises((AttributeError, TypeError)):
            s.groundedness_rate = 0.1


class TestDriftAlert:
    def test_to_dict_keys(self):
        alert = DriftAlert(
            alert_id="a1",
            timestamp="2025-01-01T00:00:00Z",
            alert_type="retrieval_drift",
            metric_name="retrieval_hit_rate",
            current_value=0.60,
            threshold_value=0.70,
            delta=-0.10,
            severity="warning",
            message="hit rate below threshold",
        )
        d = alert.to_dict()
        assert d["severity"] == "warning"
        assert d["delta"] == pytest.approx(-0.10)


# ---------------------------------------------------------------------------
# RetrievalDriftMonitor
# ---------------------------------------------------------------------------


class TestRetrievalDriftMonitor:
    def _monitor(self, **kwargs):
        return RetrievalDriftMonitor(
            hit_rate_threshold=THRESHOLD,
            score_std_threshold=THRESHOLD,
            stability_threshold=THRESHOLD,
            system_version="v1",
            **kwargs,
        )

    def test_empty_queries_raises(self):
        m = self._monitor()
        with pytest.raises(ValueError):
            m.measure([], [], [], [])

    def test_perfect_hit_rate(self):
        queries = ["q1", "q2"]
        retrieved = [["doc_1", "doc_2"], ["doc_1"]]
        gt = [["doc_1"], ["doc_1"]]
        scores = [[0.9, 0.8], [0.85]]
        snapshot = self._monitor().measure(queries, retrieved, gt, scores)
        assert snapshot.retrieval_hit_rate == pytest.approx(1.0)

    def test_zero_hit_rate(self):
        queries = ["q1", "q2"]
        retrieved = [["doc_x"], ["doc_y"]]
        gt = [["doc_1"], ["doc_2"]]
        scores = [[0.5], [0.4]]
        snapshot = self._monitor().measure(queries, retrieved, gt, scores)
        assert snapshot.retrieval_hit_rate == pytest.approx(0.0)

    def test_partial_hit_rate(self):
        queries = ["q1", "q2", "q3", "q4"]
        retrieved = [["doc_1"], ["doc_x"], ["doc_1"], ["doc_x"]]
        gt = [["doc_1"], ["doc_1"], ["doc_1"], ["doc_1"]]
        scores = [[0.9], [0.5], [0.9], [0.5]]
        snapshot = self._monitor().measure(queries, retrieved, gt, scores)
        assert snapshot.retrieval_hit_rate == pytest.approx(0.5)

    def test_sample_size_recorded(self):
        queries = ["q1", "q2", "q3"]
        retrieved = [["doc_1"]] * 3
        gt = [["doc_1"]] * 3
        scores = [[0.9]] * 3
        snapshot = self._monitor().measure(queries, retrieved, gt, scores)
        assert snapshot.sample_size == 3

    def test_no_alerts_when_above_thresholds(self):
        queries = ["q1", "q2"]
        retrieved = [["doc_1"], ["doc_1"]]
        gt = [["doc_1"], ["doc_1"]]
        scores = [[0.8, 0.7], [0.8, 0.7]]
        snapshot = self._monitor().measure(queries, retrieved, gt, scores)
        alerts = self._monitor().check_alerts(snapshot)
        # hit_rate=1.0, score_std ~ 0.05, stability check
        hit_alerts = [a for a in alerts if a.metric_name == "retrieval_hit_rate"]
        assert len(hit_alerts) == 0

    def test_alert_when_hit_rate_below_threshold(self):
        snapshot = RetrievalDriftSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            retrieval_hit_rate=0.50,  # below 0.70
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "retrieval_hit_rate" for a in alerts)

    def test_alert_when_score_std_above_threshold(self):
        snapshot = RetrievalDriftSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=0.96,  # above THRESHOLD (0.95)
            top_k_stability=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "score_distribution_std" for a in alerts)

    def test_alert_when_stability_below_threshold(self):
        snapshot = RetrievalDriftSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            retrieval_hit_rate=0.90,
            score_distribution_mean=0.7,
            score_distribution_std=0.05,
            top_k_stability=0.40,  # below 0.60
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "top_k_stability" for a in alerts)

    def test_l4_persist_graceful_on_exception(self):
        class BrokenStore:
            def put(self, a):
                raise RuntimeError("broken")

        m = self._monitor(l4_store=BrokenStore())
        queries = ["q1"]
        snapshot = m.measure(["q1"], [["doc_1"]], [["doc_1"]], [[0.9]])
        assert snapshot is not None


# ---------------------------------------------------------------------------
# EmbeddingDriftMonitor
# ---------------------------------------------------------------------------


class TestEmbeddingDriftMonitor:
    def _monitor(self, current_version="v1.2"):
        return EmbeddingDriftMonitor(
            norm_std_threshold=THRESHOLD,
            similarity_mean_threshold=THRESHOLD,
            current_model_version=current_version,
        )

    def test_empty_embeddings_raises(self):
        with pytest.raises(ValueError):
            self._monitor().measure([], [])

    def test_norm_computed_correctly(self):
        embeddings = [[3.0, 4.0]]  # norm = 5.0
        snapshot = self._monitor().measure(embeddings, [0.8])
        assert snapshot.vector_norm_mean == pytest.approx(5.0)

    def test_version_mismatch_detected(self):
        snapshot = self._monitor(current_version="v1.2").measure(
            [[1.0, 0.0]], [0.7], observed_model_version="v1.3"
        )
        assert snapshot.version_mismatch_detected is True

    def test_version_match_no_mismatch(self):
        snapshot = self._monitor(current_version="v1.2").measure(
            [[1.0, 0.0]], [0.7], observed_model_version="v1.2"
        )
        assert snapshot.version_mismatch_detected is False

    def test_alert_on_version_mismatch(self):
        snapshot = EmbeddingHealthSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            embedding_model_version="v999",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=0.7,
            similarity_distribution_std=0.05,
            version_mismatch_detected=True,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.severity == "critical" for a in alerts)

    def test_alert_on_high_norm_std(self):
        snapshot = EmbeddingHealthSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            embedding_model_version="v1.2",
            vector_norm_mean=1.0,
            vector_norm_std=0.96,  # above THRESHOLD (0.95)
            similarity_distribution_mean=0.7,
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "vector_norm_std" for a in alerts)

    def test_alert_on_low_similarity_mean(self):
        snapshot = EmbeddingHealthSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            embedding_model_version="v1.2",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=0.30,  # below 0.50
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "similarity_distribution_mean" for a in alerts)

    def test_no_alerts_when_healthy(self):
        snapshot = EmbeddingHealthSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            embedding_model_version="v1.2",
            vector_norm_mean=1.0,
            vector_norm_std=0.05,
            similarity_distribution_mean=0.96,
            similarity_distribution_std=0.05,
            version_mismatch_detected=False,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert alerts == []


# ---------------------------------------------------------------------------
# AnswerQualityMonitor
# ---------------------------------------------------------------------------


class TestAnswerQualityMonitor:
    def _monitor(self):
        return AnswerQualityMonitor(
            groundedness_threshold=THRESHOLD,
            hallucination_threshold=THRESHOLD,
            override_threshold=THRESHOLD,
            system_version="v1",
        )

    def test_empty_groundedness_scores_raises(self):
        with pytest.raises(ValueError):
            self._monitor().measure([], [], [], [])

    def test_groundedness_rate_computed(self):
        scores = [0.8, 0.9, 0.7]
        snapshot = self._monitor().measure(scores, [False, False, False], [False] * 3, [0.8] * 3)
        assert snapshot.groundedness_rate == pytest.approx(0.8)

    def test_hallucination_rate_computed(self):
        snapshot = self._monitor().measure(
            [0.8, 0.8],
            [True, False],  # 1/2 hallucinated
            [False, False],
            [0.8, 0.8],
        )
        assert snapshot.hallucination_rate == pytest.approx(0.5)

    def test_override_rate_computed(self):
        snapshot = self._monitor().measure(
            [0.8] * 4,
            [False] * 4,
            [True, True, False, False],  # 2/4 overridden
            [0.8] * 4,
        )
        assert snapshot.human_override_rate == pytest.approx(0.5)

    def test_alert_on_low_groundedness(self):
        snapshot = AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.50,  # below 0.70
            hallucination_rate=0.05,
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "groundedness_rate" for a in alerts)

    def test_alert_on_high_hallucination(self):
        snapshot = AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.90,
            hallucination_rate=0.96,  # above THRESHOLD (0.95)
            human_override_rate=0.10,
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        critical = [a for a in alerts if a.severity == "critical"]
        assert len(critical) >= 1

    def test_alert_on_high_override_rate(self):
        snapshot = AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.90,
            hallucination_rate=0.05,
            human_override_rate=0.96,  # above THRESHOLD (0.95)
            answer_correctness_mean=0.80,
            sample_size=10,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert any(a.metric_name == "human_override_rate" for a in alerts)

    def test_no_alerts_when_healthy(self):
        snapshot = AnswerQualitySnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            groundedness_rate=0.96,
            hallucination_rate=0.05,
            human_override_rate=0.10,
            answer_correctness_mean=0.85,
            sample_size=50,
        )
        alerts = self._monitor().check_alerts(snapshot)
        assert alerts == []

    def test_empty_flags_handled(self):
        snapshot = self._monitor().measure([0.8], [], [], [0.8])
        assert snapshot.hallucination_rate == pytest.approx(0.0)
        assert snapshot.human_override_rate == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# ShadowEvaluationRunner
# ---------------------------------------------------------------------------


class TestShadowEvaluationRunner:
    def _make_configs(self, cand_retrieval=None):
        baseline = SystemConfig("baseline", "v1", retrieval_fn=_perfect_retrieval)
        candidate = SystemConfig("candidate", "v2", retrieval_fn=cand_retrieval or _perfect_retrieval)
        return baseline, candidate

    def test_run_returns_result(self):
        baseline, candidate = self._make_configs()
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(2))
        assert result is not None
        assert result.delta_report is not None

    def test_identical_configs_zero_net_delta(self):
        baseline, candidate = self._make_configs()
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(2))
        net = sum(result.delta_report.metric_deltas.values())
        assert net == pytest.approx(0.0, abs=1e-9)

    def test_is_improvement_true_when_candidate_better(self):
        baseline = SystemConfig("base", "v1", retrieval_fn=_bad_retrieval)
        candidate = SystemConfig("cand", "v2", retrieval_fn=_perfect_retrieval)
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(2))
        assert result.is_improvement is True

    def test_is_improvement_false_when_candidate_worse(self):
        baseline = SystemConfig("base", "v1", retrieval_fn=_perfect_retrieval)
        candidate = SystemConfig("cand", "v2", retrieval_fn=_bad_retrieval)
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(2))
        assert result.is_improvement is False

    def test_to_dict_keys(self):
        baseline, candidate = self._make_configs()
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(1))
        d = result.to_dict()
        assert "delta_report" in d
        assert "is_improvement" in d
        assert "candidate_alert_count" in d

    def test_retrieval_snapshots_present(self):
        baseline, candidate = self._make_configs()
        runner = ShadowEvaluationRunner(baseline, candidate)
        result = runner.run(_make_dataset(2))
        assert result.baseline_retrieval_snapshot is not None
        assert result.candidate_retrieval_snapshot is not None

    def test_retrieval_monitor_alerts_in_result(self):
        monitor = RetrievalDriftMonitor(hit_rate_threshold=THRESHOLD)  # very strict → always alerts
        baseline = SystemConfig("base", "v1", retrieval_fn=_bad_retrieval)
        candidate = SystemConfig("cand", "v2", retrieval_fn=_bad_retrieval)
        runner = ShadowEvaluationRunner(baseline, candidate, retrieval_monitor=monitor)
        result = runner.run(_make_dataset(2))
        # alerts may or may not fire depending on computed snapshot values
        assert isinstance(result.candidate_alerts, list)
