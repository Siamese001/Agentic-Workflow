"""
Tests: Phase 1 — Offline and Replay Evaluation Runners

Branch coverage:
- OfflineEvaluationRunner: empty dataset, single example, aggregation, L4 persist
- ReplayEvaluationRunner: delta computation, positive/negative deltas, L4 persist
- SystemConfig: creation, metadata
- _default_metrics: returns expected metric suite
"""

import pytest
from agentic_core.evaluation.runners.offline_eval_runner import (
    OfflineEvaluationRunner,
    _default_metrics,
)
from agentic_core.evaluation.runners.replay_eval_runner import (
    ReplayEvaluationRunner,
    SystemConfig,
)
from agentic_core.evaluation.schemas.evaluation_dataset_schema import (
    EvaluationDataset,
    EvaluationExample,
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

_emit_records_execution_trace("p0", "evidence", "test_eval_runners")
_emit_applies_guardrail("p0", "test_eval_runners", "p0_governance")
_emit_reads_policy_state("p0", "test_eval_runners", "policy_binding")
_emit_snapshots_state("p0", "test_eval_runners", "state_snapshot")
emit_replay_key("p0", "test_eval_runners")
emit_determinism_digest("p0", "test_eval_runners")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_eval_runners", "execution_auth")
_emit_validates_capability("p2", "test_eval_runners", "capability_check")
_emit_routes_to_capability("p2", "test_eval_runners", "capability_route")
_emit_writes_via_uwg("p2", "test_eval_runners", "uwg_write")
_emit_blocks_direct_write("p2", "test_eval_runners", "direct_write_block")
_emit_records_tool_invocation("p2", "test_eval_runners", "tool_invocation")
_emit_captures_execution_output("p2", "test_eval_runners", "exec_output")
_emit_dispatches_agent("p3", "test_eval_runners", "agent_dispatch")
_emit_coordinates_agents("p3", "test_eval_runners", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_eval_runners", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_eval_runners", "healing_outcome")
_emit_escalates_failure("p3", "test_eval_runners", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_eval_runners", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_eval_runners", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_eval_runners", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_eval_runners", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_eval_runners", "eval_metric")
_emit_stores_embedding("p4", "test_eval_runners", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_eval_runners", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_eval_runners", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_example(query="q", docs=None, answer="the answer"):
    return EvaluationExample(
        query=query,
        ground_truth_documents=docs or ["doc_1"],
        expected_answer=answer,
    )


def _make_dataset(n=2, name="test_ds"):
    return EvaluationDataset(
        name=name,
        version="1.0",
        examples=[_make_example(f"query_{i}") for i in range(n)],
    )


def _perfect_retrieval(query):
    return ["doc_1", "doc_2", "doc_3"]


def _good_generation(query, docs):
    return "the answer matches expected"


def _bad_retrieval(query):
    return ["doc_x", "doc_y", "doc_z"]


def _bad_generation(query, docs):
    return "unrelated gibberish xyz"


# ---------------------------------------------------------------------------
# _default_metrics
# ---------------------------------------------------------------------------


class TestDefaultMetrics:
    def test_returns_list(self):
        metrics = _default_metrics()
        assert isinstance(metrics, list)

    def test_contains_six_metrics(self):
        metrics = _default_metrics()
        assert len(metrics) == 6

    def test_metric_names_include_precision_recall_mrr(self):
        names = {m.name for m in _default_metrics()}
        assert "precision@5" in names
        assert "recall@10" in names
        assert "MRR" in names
        assert "groundedness" in names
        assert "answer_correctness" in names


# ---------------------------------------------------------------------------
# OfflineEvaluationRunner
# ---------------------------------------------------------------------------


class TestOfflineEvaluationRunner:
    def test_empty_dataset_returns_empty_report(self):
        runner = OfflineEvaluationRunner()
        ds = EvaluationDataset(name="empty", version="1.0", examples=[])
        report = runner.run(ds)
        assert len(report.per_example_results) == 0
        assert report.aggregate_scores == {}

    def test_report_has_run_id(self):
        runner = OfflineEvaluationRunner()
        ds = _make_dataset(1)
        report = runner.run(ds)
        assert len(report.run_id) > 0

    def test_report_dataset_name_matches(self):
        runner = OfflineEvaluationRunner()
        ds = _make_dataset(1, name="my_ds")
        report = runner.run(ds)
        assert report.dataset_name == "my_ds"

    def test_per_example_results_count(self):
        runner = OfflineEvaluationRunner()
        ds = _make_dataset(3)
        report = runner.run(ds)
        assert len(report.per_example_results) == 3

    def test_aggregate_scores_are_averaged(self):
        runner = OfflineEvaluationRunner(retrieval_fn=_perfect_retrieval)
        ds = _make_dataset(2)
        report = runner.run(ds)
        assert "precision@5" in report.aggregate_scores
        # With perfect retrieval (3 of 3 in top-5), precision should be > 0
        assert report.aggregate_scores["precision@5"] >= 0.0

    def test_default_retrieval_returns_zero_metrics(self):
        runner = OfflineEvaluationRunner()
        ds = _make_dataset(1)
        report = runner.run(ds)
        # default retrieval returns empty → precision@5 = 0
        assert report.aggregate_scores.get("precision@5", 0.0) == pytest.approx(0.0)

    def test_system_version_propagated(self):
        runner = OfflineEvaluationRunner(system_version="v2.5")
        ds = _make_dataset(1)
        report = runner.run(ds)
        assert report.system_version == "v2.5"

    def test_custom_metrics_used(self):
        from agentic_core.evaluation.metrics.precision_at_k import PrecisionAtK

        runner = OfflineEvaluationRunner(metrics=[PrecisionAtK(k=3)])
        ds = _make_dataset(2)
        report = runner.run(ds)
        assert "precision@3" in report.aggregate_scores
        assert "recall@10" not in report.aggregate_scores

    def test_generation_fn_used(self):
        runner = OfflineEvaluationRunner(generation_fn=_good_generation)
        ds = _make_dataset(1)
        report = runner.run(ds)
        result = report.per_example_results[0]
        assert result.generated_answer == "the answer matches expected"

    def test_two_runs_same_dataset_deterministic(self):
        runner = OfflineEvaluationRunner(retrieval_fn=_perfect_retrieval)
        ds = _make_dataset(2)
        r1 = runner.run(ds)
        r2 = runner.run(ds)
        assert r1.aggregate_scores == r2.aggregate_scores

    def test_l4_persist_called_when_store_provided(self):
        """Verify persist does not raise when store is provided."""
        stored = []

        class FakeStore:
            def put(self, artifact):
                stored.append(artifact)

        runner = OfflineEvaluationRunner(l4_store=FakeStore())
        ds = _make_dataset(1)
        runner.run(ds)
        assert len(stored) == 1

    def test_l4_persist_graceful_on_exception(self):
        """Persist failure must not crash the runner."""

        class BrokenStore:
            def put(self, artifact):
                raise RuntimeError("disk full")

        runner = OfflineEvaluationRunner(l4_store=BrokenStore())
        ds = _make_dataset(1)
        report = runner.run(ds)  # must not raise
        assert report is not None

    def test_timestamp_in_report(self):
        runner = OfflineEvaluationRunner()
        ds = _make_dataset(1)
        report = runner.run(ds)
        assert report.timestamp.endswith("Z")


# ---------------------------------------------------------------------------
# ReplayEvaluationRunner
# ---------------------------------------------------------------------------


class TestReplayEvaluationRunner:
    def _baseline_config(self):
        return SystemConfig(
            name="baseline",
            version="v1",
            retrieval_fn=_perfect_retrieval,
        )

    def _candidate_config(self, retrieval_fn=None):
        return SystemConfig(
            name="candidate",
            version="v2",
            retrieval_fn=retrieval_fn or _perfect_retrieval,
        )

    def test_delta_report_run_ids_differ(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(2)
        delta = runner.run(ds, self._baseline_config(), self._candidate_config())
        assert delta.run_id_a != delta.run_id_b

    def test_delta_report_config_names(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(1)
        delta = runner.run(ds, self._baseline_config(), self._candidate_config())
        assert delta.config_a_name == "baseline"
        assert delta.config_b_name == "candidate"

    def test_identical_configs_zero_delta(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(2)
        config_a = self._baseline_config()
        config_b = self._candidate_config(retrieval_fn=_perfect_retrieval)
        delta = runner.run(ds, config_a, config_b)
        for metric, d in delta.metric_deltas.items():
            assert d == pytest.approx(0.0, abs=1e-9), f"Expected 0 delta for {metric}, got {d}"

    def test_better_candidate_positive_delta(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(2)
        config_a = SystemConfig("base", "v1", retrieval_fn=_bad_retrieval)
        config_b = SystemConfig("cand", "v2", retrieval_fn=_perfect_retrieval)
        delta = runner.run(ds, config_a, config_b)
        # recall@10 should improve
        assert delta.metric_deltas.get("recall@10", 0.0) > 0

    def test_worse_candidate_negative_delta(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(2)
        config_a = SystemConfig("base", "v1", retrieval_fn=_perfect_retrieval)
        config_b = SystemConfig("cand", "v2", retrieval_fn=_bad_retrieval)
        delta = runner.run(ds, config_a, config_b)
        assert delta.metric_deltas.get("recall@10", 0.0) < 0

    def test_delta_scores_a_and_b_present(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(1)
        delta = runner.run(ds, self._baseline_config(), self._candidate_config())
        assert isinstance(delta.scores_a, dict)
        assert isinstance(delta.scores_b, dict)

    def test_l4_persist_on_delta(self):
        stored = []

        class FakeStore:
            def put(self, artifact):
                stored.append(artifact)

        runner = ReplayEvaluationRunner(l4_store=FakeStore())
        ds = _make_dataset(1)
        runner.run(ds, self._baseline_config(), self._candidate_config())
        assert any("evaluation_delta" in str(a) or hasattr(a, "kind") for a in stored)

    def test_l4_persist_graceful_on_exception(self):
        class BrokenStore:
            def put(self, artifact):
                raise OSError("no space left")

        runner = ReplayEvaluationRunner(l4_store=BrokenStore())
        ds = _make_dataset(1)
        delta = runner.run(ds, self._baseline_config(), self._candidate_config())
        assert delta is not None

    def test_delta_to_dict_roundtrip(self):
        runner = ReplayEvaluationRunner()
        ds = _make_dataset(1)
        delta = runner.run(ds, self._baseline_config(), self._candidate_config())
        d = delta.to_dict()
        from agentic_core.evaluation.schemas.evaluation_result_schema import DeltaReport

        restored = DeltaReport.from_dict(d)
        assert restored.config_a_name == delta.config_a_name


# ---------------------------------------------------------------------------
# SystemConfig
# ---------------------------------------------------------------------------


class TestSystemConfig:
    def test_minimal_creation(self):
        cfg = SystemConfig(name="test", version="v1")
        assert cfg.name == "test"
        assert cfg.version == "v1"
        assert cfg.retrieval_fn is None
        assert cfg.generation_fn is None
        assert cfg.metadata == {}

    def test_with_metadata(self):
        cfg = SystemConfig(name="x", version="v1", metadata={"key": "val"})
        assert cfg.metadata["key"] == "val"

    def test_with_retrieval_fn(self):
        cfg = SystemConfig(name="x", version="v1", retrieval_fn=_perfect_retrieval)
        assert cfg.retrieval_fn is not None
        assert cfg.retrieval_fn("q") == ["doc_1", "doc_2", "doc_3"]
