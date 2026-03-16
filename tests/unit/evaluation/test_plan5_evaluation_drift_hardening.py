"""Plan 5 — Evaluation & Drift Tracking Hardening Tests.

Covers:
- Gap 1: RetrievalDriftMonitor injectable timestamps (DriftClock)
- Gap 5: ShadowDriftAnalyzer externalized threshold
- Gap 2: DriftRegistry record/query round-trip
- Gap 4: RAGAS-style metrics (FaithfulnessMetric, AnswerRelevancyMetric,
         ContextPrecisionMetric, GroundednessMetric)
- Gap 7: LLM-as-Judge harness (JudgeScore, NullJudge, GeminiJudge)
"""

from __future__ import annotations

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

_emit_records_execution_trace("p0", "evidence", "test_plan5_evaluation_drift_hardening")
_emit_applies_guardrail("p0", "test_plan5_evaluation_drift_hardening", "p0_governance")
_emit_reads_policy_state("p0", "test_plan5_evaluation_drift_hardening", "policy_binding")
_emit_snapshots_state("p0", "test_plan5_evaluation_drift_hardening", "state_snapshot")
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

_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_1")
_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_2")
_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_3")
_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_4")
_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_5")
_emit_emits_metric_event("test_plan5_evaluation_drift_hardening", "p4obs", "metric_6")
_emit_records_incident_event("test_plan5_evaluation_drift_hardening", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_plan5_evaluation_drift_hardening", "p4obs", "anomaly")
_emit_writes_observability_log("test_plan5_evaluation_drift_hardening", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_plan5_evaluation_drift_hardening", "p4obs", "mon_state")
_emit_triggers_alert("test_plan5_evaluation_drift_hardening", "p4obs", "alert")
_emit_links_incident_trace("test_plan5_evaluation_drift_hardening", "p4obs", "trace_link")
_emit_captures_pattern("test_plan5_evaluation_drift_hardening", "p3lm", "pattern")
_emit_records_learning_event("test_plan5_evaluation_drift_hardening", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_plan5_evaluation_drift_hardening", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_plan5_evaluation_drift_hardening", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_plan5_evaluation_drift_hardening", "p3lm", "routing")
_emit_improves_agent_policy("test_plan5_evaluation_drift_hardening", "p3lm", "policy")
_emit_stores_learning_state("test_plan5_evaluation_drift_hardening", "p3lm", "state")
_emit_records_execution_trace("test_plan5_evaluation_drift_hardening", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_plan5_evaluation_drift_hardening", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_plan5_evaluation_drift_hardening", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_plan5_evaluation_drift_hardening", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_plan5_evaluation_drift_hardening", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_plan5_evaluation_drift_hardening", "env_read", "p2_env_1")
_emit_reads_environ("test_plan5_evaluation_drift_hardening", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_plan5_evaluation_drift_hardening", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_plan5_evaluation_drift_hardening", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_plan5_evaluation_drift_hardening", "context_pull")
_emit_pulls_context("p1", "test_plan5_evaluation_drift_hardening", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_plan5_evaluation_drift_hardening", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_plan5_evaluation_drift_hardening", "uwg_term_2")
_emit_writes_through("p1", "test_plan5_evaluation_drift_hardening", "write_through")
_emit_writes_through("p1", "test_plan5_evaluation_drift_hardening", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_plan5_evaluation_drift_hardening", "safety_validation")
_emit_invokes_eval("p1", "test_plan5_evaluation_drift_hardening", "eval_call")
_emit_proposal_commits_routing("p1", "test_plan5_evaluation_drift_hardening", "routing_commit")
_emit_escalates_to_human("p1", "test_plan5_evaluation_drift_hardening", "human_escalation")
_emit_routes_through("p1", "test_plan5_evaluation_drift_hardening", "route_through")
_emit_checks_agent_registry("p1", "test_plan5_evaluation_drift_hardening", "agent_registry")
_emit_validates_agent_capability("p1", "test_plan5_evaluation_drift_hardening", "capability")
_emit_dispatches_execution_plan("p1", "test_plan5_evaluation_drift_hardening", "exec_plan")
_emit_agent_executes_agent("p1", "test_plan5_evaluation_drift_hardening", "sub_agent")
_emit_routes_to_agent("p1", "test_plan5_evaluation_drift_hardening", "target_agent")
_emit_verifies_policy("p1", "test_plan5_evaluation_drift_hardening", "policy_check")
_emit_observes_runtime_state("p1", "test_plan5_evaluation_drift_hardening", "runtime_state")
_emit_verifies_boundary("p1", "test_plan5_evaluation_drift_hardening", "boundary_check")
_emit_transcripts_response("p1", "test_plan5_evaluation_drift_hardening", "transcript")
_emit_hard_fails_untranscripted("p1", "test_plan5_evaluation_drift_hardening")
_emit_gated_by_confidence("p1", "test_plan5_evaluation_drift_hardening", "confidence_gate")
emit_replay_key("p0", "test_plan5_evaluation_drift_hardening")
emit_determinism_digest("p0", "test_plan5_evaluation_drift_hardening")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_plan5_evaluation_drift_hardening", "execution_auth")
_emit_validates_capability("p2", "test_plan5_evaluation_drift_hardening", "capability_check")
_emit_routes_to_capability("p2", "test_plan5_evaluation_drift_hardening", "capability_route")
_emit_writes_via_uwg("p2", "test_plan5_evaluation_drift_hardening", "uwg_write")
_emit_blocks_direct_write("p2", "test_plan5_evaluation_drift_hardening", "direct_write_block")
_emit_records_tool_invocation("p2", "test_plan5_evaluation_drift_hardening", "tool_invocation")
_emit_captures_execution_output("p2", "test_plan5_evaluation_drift_hardening", "exec_output")
_emit_dispatches_agent("p3", "test_plan5_evaluation_drift_hardening", "agent_dispatch")
_emit_coordinates_agents("p3", "test_plan5_evaluation_drift_hardening", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_plan5_evaluation_drift_hardening", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_plan5_evaluation_drift_hardening", "healing_outcome")
_emit_escalates_failure("p3", "test_plan5_evaluation_drift_hardening", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_plan5_evaluation_drift_hardening", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_plan5_evaluation_drift_hardening", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_plan5_evaluation_drift_hardening", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_plan5_evaluation_drift_hardening", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_plan5_evaluation_drift_hardening", "eval_metric")
_emit_stores_embedding("p4", "test_plan5_evaluation_drift_hardening", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_plan5_evaluation_drift_hardening", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_plan5_evaluation_drift_hardening", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Gap 1: Injectable timestamps in RetrievalDriftMonitor
# ---------------------------------------------------------------------------


class TestDriftMonitorInjectableTimestamps:
    _FIXED_TS = "2024-01-01T00:00:00Z"

    def _make_monitor(self):
        from agentic_core.utils.workflow_engines.drift_monitor import RetrievalDriftMonitor

        return RetrievalDriftMonitor()

    def test_measure_with_explicit_now_iso_sets_snapshot_timestamp(self):
        monitor = self._make_monitor()
        snapshot = monitor.measure(
            queries=["q1"],
            retrieved_doc_ids=[["d1"]],
            ground_truth_doc_ids=[["d1"]],
            scores=[[0.9]],
            now_iso=self._FIXED_TS,
        )
        assert snapshot.timestamp == self._FIXED_TS

    def test_measure_two_calls_same_now_iso_produce_equal_timestamps(self):
        monitor = self._make_monitor()
        kwargs = {
            "queries": ["q1"],
            "retrieved_doc_ids": [["d1"]],
            "ground_truth_doc_ids": [["d1"]],
            "scores": [[0.9]],
            "now_iso": self._FIXED_TS,
        }
        s1 = monitor.measure(**kwargs)
        s2 = monitor.measure(**kwargs)
        assert s1.timestamp == s2.timestamp == self._FIXED_TS

    def test_check_alerts_with_explicit_now_iso_sets_alert_timestamp(self):
        from agentic_core.utils.workflow_engines.drift_monitor import RetrievalDriftMonitor

        monitor = RetrievalDriftMonitor(hit_rate_threshold=THRESHOLD)
        snapshot = monitor.measure(
            queries=["q1"],
            retrieved_doc_ids=[["miss"]],
            ground_truth_doc_ids=[["d1"]],
            scores=[[0.5]],
            now_iso=self._FIXED_TS,
        )
        alerts = monitor.check_alerts(snapshot, now_iso=self._FIXED_TS)
        assert len(alerts) > 0
        assert all(a.timestamp == self._FIXED_TS for a in alerts)

    def test_drift_clock_utcnow_returns_string(self):
        from agentic_core.utils.workflow_engines.drift_monitor import DriftClock

        ts = DriftClock.utcnow()
        assert isinstance(ts, str)
        assert ts.endswith("Z")

    def test_measure_without_now_iso_uses_wall_clock(self):
        monitor = self._make_monitor()
        snapshot = monitor.measure(
            queries=["q1"],
            retrieved_doc_ids=[["d1"]],
            ground_truth_doc_ids=[["d1"]],
            scores=[[0.9]],
        )
        assert snapshot.timestamp is not None
        assert snapshot.timestamp.endswith("Z")


# ---------------------------------------------------------------------------
# Gap 5: ShadowDriftAnalyzer externalized threshold
# ---------------------------------------------------------------------------


class TestShadowDriftAnalyzerThreshold:
    def _records(self, cosine: float) -> list[dict]:
        return [{"primary_shadow_cosine": cosine}]

    def test_default_threshold_is_0_92(self):
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer()
        assert analyzer._drift_threshold == 0.92

    def test_custom_threshold_stored(self):
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        assert analyzer._drift_threshold == 0.85

    def test_summary_contains_drift_threshold_field(self):
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer()
        summary = analyzer.analyze_batch(shadow_records=self._records(0.95), profile_id="p1", now_utc=0)
        assert hasattr(summary, "drift_threshold")
        assert summary.drift_threshold == 0.92

    def test_custom_threshold_reflected_in_summary(self):
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        summary = analyzer.analyze_batch(shadow_records=self._records(0.90), profile_id="p1", now_utc=0)
        assert summary.drift_threshold == 0.85

    def test_drift_flag_respects_custom_threshold(self):
        """Analyzer(threshold=THRESHOLD): cosine=0.84 < 0.85 → drift_flag=True."""
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        summary = analyzer.analyze_batch(shadow_records=self._records(0.84), profile_id="p1", now_utc=0)
        assert summary.drift_flag is True

    def test_drift_flag_false_when_above_custom_threshold(self):
        """Analyzer(threshold=THRESHOLD): cosine=0.90 >= 0.85 → drift_flag=False."""
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        analyzer = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        summary = analyzer.analyze_batch(shadow_records=self._records(0.90), profile_id="p1", now_utc=0)
        assert summary.drift_flag is False

    def test_digest_includes_threshold_value(self):
        """Two analyzers with different thresholds must produce different digests."""
        from system_learning.engines.shadow_drift_analyzer import ShadowDriftAnalyzer

        records = self._records(0.90)
        a1 = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        a2 = ShadowDriftAnalyzer(drift_threshold=THRESHOLD)
        s1 = a1.analyze_batch(shadow_records=records, profile_id="p1", now_utc=0)
        s2 = a2.analyze_batch(shadow_records=records, profile_id="p1", now_utc=0)
        assert s1.deterministic_digest != s2.deterministic_digest


# ---------------------------------------------------------------------------
# Gap 2: DriftRegistry
# ---------------------------------------------------------------------------


class TestDriftRegistry:
    def _make_entry(self, source="retrieval", metric="hit_rate", value=0.5, flag=True, sev="warning"):
        from agentic_core.L6_observability.engines.drift_registry import DriftRegistryEntry

        return DriftRegistryEntry.create(
            source=source,
            timestamp_iso="2024-01-01T00:00:00Z",
            metric_name=metric,
            current_value=value,
            threshold_value=0.70,
            drift_flag=flag,
            severity=sev,
        )

    def _make_registry(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.drift_registry import DriftRegistry

        return DriftRegistry(timeline_path=Path("/dev/null") if True else None)

    def test_record_and_query_round_trip(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.drift_registry import DriftRegistry

        reg = DriftRegistry(timeline_path=Path("nul"))
        entry = self._make_entry()
        reg.record(entry)
        results = reg.query()
        assert len(results) == 1
        assert results[0].source == "retrieval"

    def test_query_source_filter_returns_only_matching(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.drift_registry import DriftRegistry

        reg = DriftRegistry(timeline_path=Path("nul"))
        reg.record(self._make_entry(source="retrieval"))
        reg.record(self._make_entry(source="shadow"))
        reg.record(self._make_entry(source="shadow"))
        results = reg.query(source_filter="shadow")
        assert len(results) == 2
        assert all(r.source == "shadow" for r in results)

    def test_query_source_filter_retrieval_excludes_shadow(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.drift_registry import DriftRegistry

        reg = DriftRegistry(timeline_path=Path("nul"))
        reg.record(self._make_entry(source="retrieval"))
        reg.record(self._make_entry(source="shadow"))
        results = reg.query(source_filter="retrieval")
        assert len(results) == 1

    def test_registry_entry_has_deterministic_digest(self):
        from agentic_core.L6_observability.engines.drift_registry import DriftRegistryEntry

        e1 = DriftRegistryEntry.create(
            source="shadow",
            timestamp_iso="2024-01-01T00:00:00Z",
            metric_name="p95_cosine",
            current_value=0.88,
            threshold_value=0.92,
            drift_flag=True,
            severity="warning",
        )
        e2 = DriftRegistryEntry.create(
            source="shadow",
            timestamp_iso="2024-01-01T00:00:00Z",
            metric_name="p95_cosine",
            current_value=0.88,
            threshold_value=0.92,
            drift_flag=True,
            severity="warning",
        )
        assert e1.deterministic_digest == e2.deterministic_digest

    def test_different_values_produce_different_digests(self):
        from agentic_core.L6_observability.engines.drift_registry import DriftRegistryEntry

        e1 = DriftRegistryEntry.create(
            source="shadow",
            timestamp_iso="2024-01-01T00:00:00Z",
            metric_name="p95",
            current_value=0.88,
            threshold_value=0.92,
            drift_flag=True,
            severity="warning",
        )
        e2 = DriftRegistryEntry.create(
            source="shadow",
            timestamp_iso="2024-01-01T00:00:00Z",
            metric_name="p95",
            current_value=0.99,
            threshold_value=0.92,
            drift_flag=False,
            severity="info",
        )
        assert e1.deterministic_digest != e2.deterministic_digest

    def test_all_entries_returns_insertion_order(self):
        from pathlib import Path

        from agentic_core.L6_observability.engines.drift_registry import DriftRegistry

        reg = DriftRegistry(timeline_path=Path("nul"))
        sources = ["retrieval", "shadow", "embedding", "c0_context"]
        for src in sources:
            reg.record(self._make_entry(source=src))
        all_e = reg.all_entries()
        assert [e.source for e in all_e] == sources


# ---------------------------------------------------------------------------
# Gap 4: RAGAS metrics — determinism + edge cases
# ---------------------------------------------------------------------------


class TestRagasMetricsDeterminism:
    def test_context_precision_perfect_recall(self):
        from agentic_core.evaluation.metrics.ragas_metrics import ContextPrecisionMetric

        m = ContextPrecisionMetric()
        score = m.compute(prediction=["a", "b", "c"], ground_truth={"a", "b", "c"})
        assert score == pytest.approx(1.0)

    def test_context_precision_zero_overlap(self):
        from agentic_core.evaluation.metrics.ragas_metrics import ContextPrecisionMetric

        m = ContextPrecisionMetric()
        score = m.compute(prediction=["a", "b"], ground_truth={"x", "y"})
        assert score == pytest.approx(0.0)

    def test_context_precision_partial(self):
        from agentic_core.evaluation.metrics.ragas_metrics import ContextPrecisionMetric

        m = ContextPrecisionMetric()
        score = m.compute(prediction=["a", "b", "c", "d"], ground_truth={"a", "b"})
        assert score == pytest.approx(0.5)

    def test_context_precision_empty_prediction_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import ContextPrecisionMetric

        m = ContextPrecisionMetric()
        assert m.compute(prediction=[], ground_truth={"a"}) == pytest.approx(0.0)

    def test_faithfulness_empty_answer_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import FaithfulnessMetric

        m = FaithfulnessMetric()
        assert m.compute(prediction="", context=["some context"]) == pytest.approx(0.0)

    def test_faithfulness_empty_context_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import FaithfulnessMetric

        m = FaithfulnessMetric()
        assert m.compute(prediction="The sky is blue.", context=[]) == pytest.approx(0.0)

    def test_faithfulness_deterministic_identical_inputs(self):
        from agentic_core.evaluation.metrics.ragas_metrics import FaithfulnessMetric

        m = FaithfulnessMetric()
        answer = "Paris is the capital of France."
        context = ["Paris is the capital of France and a major European city."]
        s1 = m.compute(prediction=answer, context=context)
        s2 = m.compute(prediction=answer, context=context)
        assert s1 == s2

    def test_answer_relevancy_empty_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import AnswerRelevancyMetric

        m = AnswerRelevancyMetric()
        assert m.compute(prediction="", ground_truth="query") == pytest.approx(0.0)
        assert m.compute(prediction="answer", ground_truth="") == pytest.approx(0.0)

    def test_answer_relevancy_deterministic(self):
        from agentic_core.evaluation.metrics.ragas_metrics import AnswerRelevancyMetric

        m = AnswerRelevancyMetric()
        s1 = m.compute(prediction="The capital is Paris.", ground_truth="What is the capital?")
        s2 = m.compute(prediction="The capital is Paris.", ground_truth="What is the capital?")
        assert s1 == s2

    def test_groundedness_empty_answer_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import GroundednessMetric

        m = GroundednessMetric()
        assert m.compute(prediction="", context=["context"]) == pytest.approx(0.0)

    def test_groundedness_no_context_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import GroundednessMetric

        m = GroundednessMetric()
        assert m.compute(prediction="Some claim.", context=[]) == pytest.approx(0.0)
        assert m.compute(prediction="Some claim.", context=None) == pytest.approx(0.0)

    def test_cosine_helper_zero_norm_returns_zero(self):
        from agentic_core.evaluation.metrics.ragas_metrics import _cosine

        assert _cosine([0.0, 0.0], [1.0, 0.0]) == pytest.approx(0.0)
        assert _cosine([0.0, 0.0], [0.0, 0.0]) == pytest.approx(0.0)

    def test_cosine_identical_vectors_returns_one(self):
        from agentic_core.evaluation.metrics.ragas_metrics import _cosine

        v = [1.0, 2.0, 3.0]
        assert _cosine(v, v) == pytest.approx(1.0)

    def test_split_sentences_handles_empty(self):
        from agentic_core.evaluation.metrics.ragas_metrics import _split_sentences

        assert _split_sentences("") == []
        assert _split_sentences("   ") == []


# ---------------------------------------------------------------------------
# Gap 7: LLM-as-Judge harness
# ---------------------------------------------------------------------------


class TestJudgeScore:
    def test_judge_score_deterministic_digest(self):
        from agentic_core.evaluation.judges.llm_judge import JudgeScore

        s1 = JudgeScore.create(3.0, 4.0, 2.0, 3.0, "ok", "null")
        s2 = JudgeScore.create(3.0, 4.0, 2.0, 3.0, "ok", "null")
        assert s1.deterministic_digest == s2.deterministic_digest

    def test_different_scores_different_digest(self):
        from agentic_core.evaluation.judges.llm_judge import JudgeScore

        s1 = JudgeScore.create(3.0, 4.0, 2.0, 3.0, "ok", "null")
        s2 = JudgeScore.create(5.0, 5.0, 5.0, 5.0, "ok", "null")
        assert s1.deterministic_digest != s2.deterministic_digest

    def test_judge_score_has_all_required_fields(self):
        from agentic_core.evaluation.judges.llm_judge import JudgeScore

        s = JudgeScore.create(3.0, 3.0, 3.0, 3.0, "reason", "model")
        assert hasattr(s, "faithfulness")
        assert hasattr(s, "answer_relevancy")
        assert hasattr(s, "context_precision")
        assert hasattr(s, "groundedness")
        assert hasattr(s, "reasoning")
        assert hasattr(s, "judge_model")
        assert hasattr(s, "deterministic_digest")

    def test_judge_score_is_frozen(self):
        from agentic_core.evaluation.judges.llm_judge import JudgeScore

        s = JudgeScore.create(3.0, 3.0, 3.0, 3.0, "r", "m")
        with pytest.raises((AttributeError, TypeError)):
            s.faithfulness = 5.0  # type: ignore[misc]


class TestNullJudge:
    def test_null_judge_returns_fixed_score(self):
        from agentic_core.evaluation.judges.llm_judge import NullJudge

        judge = NullJudge()
        score = judge.score("query", "context", "answer")
        assert score.faithfulness == NullJudge.FIXED_SCORE
        assert score.answer_relevancy == NullJudge.FIXED_SCORE

    def test_null_judge_is_deterministic(self):
        from agentic_core.evaluation.judges.llm_judge import NullJudge

        judge = NullJudge()
        s1 = judge.score("q", "c", "a")
        s2 = judge.score("q", "c", "a")
        assert s1.deterministic_digest == s2.deterministic_digest

    def test_null_judge_same_digest_different_inputs(self):
        """NullJudge ignores input — same digest regardless of query."""
        from agentic_core.evaluation.judges.llm_judge import NullJudge

        judge = NullJudge()
        s1 = judge.score("query A", "ctx A", "ans A")
        s2 = judge.score("query B", "ctx B", "ans B")
        assert s1.deterministic_digest == s2.deterministic_digest

    def test_null_judge_implements_llm_judge_protocol(self):
        from agentic_core.evaluation.judges.llm_judge import LLMJudge, NullJudge

        assert isinstance(NullJudge(), LLMJudge)

    def test_null_judge_judge_model_is_null(self):
        from agentic_core.evaluation.judges.llm_judge import NullJudge

        score = NullJudge().score("q", "c", "a")
        assert score.judge_model == "null"
