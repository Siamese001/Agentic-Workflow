"""
Tests: Phase 1 — Evaluation Schemas

Branch coverage:
- EvaluationExample: to_dict, from_dict, roundtrip
- EvaluationDataset: to_dict, from_dict, len, roundtrip
- EvaluationResult: to_dict, from_dict, frozen
- EvaluationReport: to_dict, from_dict, frozen
- EvaluationSnapshot: to_dict, from_dict
- DeltaReport: to_dict, from_dict
- SystemEvaluationSummary: overall_score, from_report
- ComparativeEvaluationSummary: from_delta_report, promote/reject
"""

import pytest
from agentic_core.evaluation.schemas.evaluation_dataset_schema import (
    EvaluationDataset,
    EvaluationExample,
)
from agentic_core.evaluation.schemas.evaluation_report_schema import (
    ComparativeEvaluationSummary,
    SystemEvaluationSummary,
)
from agentic_core.evaluation.schemas.evaluation_result_schema import (
    DeltaReport,
    EvaluationReport,
    EvaluationResult,
    EvaluationSnapshot,
)

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_eval_schemas")
_emit_applies_guardrail("p0", "test_eval_schemas", "p0_governance")
_emit_reads_policy_state("p0", "test_eval_schemas", "policy_binding")
_emit_snapshots_state("p0", "test_eval_schemas", "state_snapshot")
emit_replay_key("p0", "test_eval_schemas")
emit_determinism_digest("p0", "test_eval_schemas")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# ---------------------------------------------------------------------------
# EvaluationExample
# ---------------------------------------------------------------------------


class TestEvaluationExample:
    def _make(self, **kwargs):
        defaults = {
            "query": "q",
            "ground_truth_documents": ["doc_1"],
            "expected_answer": "expected",
            "metadata": {"source": "test"},
        }
        defaults.update(kwargs)
        return EvaluationExample(**defaults)

    def test_to_dict_roundtrip(self):
        ex = self._make()
        d = ex.to_dict()
        restored = EvaluationExample.from_dict(d)
        assert restored.query == ex.query
        assert restored.ground_truth_documents == ex.ground_truth_documents
        assert restored.expected_answer == ex.expected_answer
        assert restored.metadata == ex.metadata

    def test_from_dict_missing_metadata_defaults_empty(self):
        d = {"query": "q", "ground_truth_documents": ["doc_1"], "expected_answer": "a"}
        ex = EvaluationExample.from_dict(d)
        assert ex.metadata == {}

    def test_to_dict_keys(self):
        ex = self._make()
        d = ex.to_dict()
        assert set(d.keys()) == {"query", "ground_truth_documents", "expected_answer", "metadata"}

    def test_empty_ground_truth(self):
        ex = self._make(ground_truth_documents=[])
        assert ex.ground_truth_documents == []

    def test_multiple_ground_truth_docs(self):
        ex = self._make(ground_truth_documents=["doc_1", "doc_2", "doc_3"])
        d = ex.to_dict()
        assert d["ground_truth_documents"] == ["doc_1", "doc_2", "doc_3"]


# ---------------------------------------------------------------------------
# EvaluationDataset
# ---------------------------------------------------------------------------


class TestEvaluationDataset:
    def _make_example(self, query="q"):
        return EvaluationExample(
            query=query,
            ground_truth_documents=["doc_1"],
            expected_answer="ans",
        )

    def _make_dataset(self, n=2):
        return EvaluationDataset(
            name="test_ds",
            version="1.0",
            description="test",
            examples=[self._make_example(f"q{i}") for i in range(n)],
        )

    def test_len(self):
        ds = self._make_dataset(3)
        assert len(ds) == 3

    def test_len_empty(self):
        ds = EvaluationDataset(name="empty", version="1.0", examples=[])
        assert len(ds) == 0

    def test_to_dict_roundtrip(self):
        ds = self._make_dataset(2)
        d = ds.to_dict()
        restored = EvaluationDataset.from_dict(d)
        assert restored.name == ds.name
        assert restored.version == ds.version
        assert len(restored.examples) == 2

    def test_from_dict_missing_description_defaults_empty(self):
        d = {"name": "n", "version": "1.0", "examples": []}
        ds = EvaluationDataset.from_dict(d)
        assert ds.description == ""

    def test_to_dict_contains_examples(self):
        ds = self._make_dataset(1)
        d = ds.to_dict()
        assert len(d["examples"]) == 1
        assert "query" in d["examples"][0]


# ---------------------------------------------------------------------------
# EvaluationResult
# ---------------------------------------------------------------------------


class TestEvaluationResult:
    def _make(self, **kwargs):
        defaults = {
            "example_id": "ex_0",
            "query": "q",
            "retrieved_doc_ids": ["doc_1"],
            "generated_answer": "ans",
            "metric_scores": {"precision@5": 0.8},
            "metadata": {},
        }
        defaults.update(kwargs)
        return EvaluationResult(**defaults)

    def test_to_dict_roundtrip(self):
        r = self._make()
        d = r.to_dict()
        restored = EvaluationResult.from_dict(d)
        assert restored.example_id == r.example_id
        assert restored.metric_scores == r.metric_scores

    def test_frozen_immutable(self):
        r = self._make()
        with pytest.raises((AttributeError, TypeError)):
            r.query = "changed"

    def test_empty_retrieved_docs(self):
        r = self._make(retrieved_doc_ids=[])
        assert r.retrieved_doc_ids == []

    def test_multiple_metrics(self):
        r = self._make(metric_scores={"precision@5": 0.8, "recall@10": 0.9, "MRR": 0.7})
        d = r.to_dict()
        assert len(d["metric_scores"]) == 3


# ---------------------------------------------------------------------------
# EvaluationReport
# ---------------------------------------------------------------------------


class TestEvaluationReport:
    def _make_result(self, eid="ex_0"):
        return EvaluationResult(
            example_id=eid,
            query="q",
            retrieved_doc_ids=["doc_1"],
            generated_answer="ans",
            metric_scores={"precision@5": 0.8},
        )

    def _make_report(self, n_results=2):
        return EvaluationReport(
            run_id="run_001",
            dataset_name="test_ds",
            dataset_version="1.0",
            system_version="v1",
            timestamp="2025-01-01T00:00:00Z",
            aggregate_scores={"precision@5": 0.8},
            per_example_results=[self._make_result(f"ex_{i}") for i in range(n_results)],
        )

    def test_to_dict_roundtrip(self):
        r = self._make_report()
        d = r.to_dict()
        restored = EvaluationReport.from_dict(d)
        assert restored.run_id == r.run_id
        assert len(restored.per_example_results) == 2

    def test_frozen_immutable(self):
        r = self._make_report()
        with pytest.raises((AttributeError, TypeError)):
            r.run_id = "changed"

    def test_empty_results(self):
        r = self._make_report(n_results=0)
        assert len(r.per_example_results) == 0

    def test_aggregate_scores_preserved(self):
        r = self._make_report()
        d = r.to_dict()
        assert d["aggregate_scores"]["precision@5"] == 0.8


# ---------------------------------------------------------------------------
# EvaluationSnapshot
# ---------------------------------------------------------------------------


class TestEvaluationSnapshot:
    def _make(self):
        return EvaluationSnapshot(
            timestamp="2025-01-01T00:00:00Z",
            system_version="v1",
            dataset_version="1.0",
            metric_results={"precision@5": 0.8},
            run_id="run_001",
        )

    def test_to_dict_roundtrip(self):
        s = self._make()
        d = s.to_dict()
        restored = EvaluationSnapshot.from_dict(d)
        assert restored.run_id == s.run_id
        assert restored.metric_results == s.metric_results

    def test_frozen(self):
        s = self._make()
        with pytest.raises((AttributeError, TypeError)):
            s.run_id = "x"

    def test_missing_metadata_defaults(self):
        d = {
            "timestamp": "2025-01-01T00:00:00Z",
            "system_version": "v1",
            "dataset_version": "1.0",
            "metric_results": {},
            "run_id": "r",
        }
        s = EvaluationSnapshot.from_dict(d)
        assert s.metadata == {}


# ---------------------------------------------------------------------------
# DeltaReport
# ---------------------------------------------------------------------------


class TestDeltaReport:
    def _make(self, net=0.12):
        return DeltaReport(
            run_id_a="run_a",
            run_id_b="run_b",
            config_a_name="baseline",
            config_b_name="candidate",
            timestamp="2025-01-01T00:00:00Z",
            metric_deltas={"precision@5": net},
            scores_a={"precision@5": 0.7},
            scores_b={"precision@5": 0.7 + net},
        )

    def test_to_dict_roundtrip(self):
        delta = self._make()
        d = delta.to_dict()
        restored = DeltaReport.from_dict(d)
        assert restored.run_id_a == "run_a"
        assert restored.metric_deltas["precision@5"] == pytest.approx(0.12)

    def test_negative_delta(self):
        delta = self._make(net=-0.05)
        assert delta.metric_deltas["precision@5"] < 0

    def test_frozen(self):
        delta = self._make()
        with pytest.raises((AttributeError, TypeError)):
            delta.run_id_a = "x"


# ---------------------------------------------------------------------------
# SystemEvaluationSummary
# ---------------------------------------------------------------------------


class TestSystemEvaluationSummary:
    def _make_report(self, scores=None):
        if scores is None:
            scores = {
                "precision@5": 0.80,
                "answer_correctness": 0.75,
                "safety_compliance": 1.0,
                "hallucination_risk": 0.05,
            }
        return EvaluationReport(
            run_id="run_001",
            dataset_name="test",
            dataset_version="1.0",
            system_version="v1",
            timestamp="2025-01-01T00:00:00Z",
            aggregate_scores=scores,
            per_example_results=[],
        )

    def test_from_report_uses_correct_fields(self):
        report = self._make_report()
        summary = SystemEvaluationSummary.from_report(report)
        assert summary.retrieval_quality_score == pytest.approx(0.80)
        assert summary.answer_quality_score == pytest.approx(0.75)

    def test_overall_score_is_composite(self):
        summary = SystemEvaluationSummary(
            system_version="v1",
            dataset_name="test",
            retrieval_quality_score=1.0,
            answer_quality_score=1.0,
            safety_compliance_score=1.0,
            hallucination_risk_score=0.0,
            timestamp="2025-01-01T00:00:00Z",
            run_id="r",
        )
        assert summary.overall_score == pytest.approx(1.0)

    def test_overall_score_penalized_by_hallucination(self):
        summary = SystemEvaluationSummary(
            system_version="v1",
            dataset_name="test",
            retrieval_quality_score=1.0,
            answer_quality_score=1.0,
            safety_compliance_score=1.0,
            hallucination_risk_score=1.0,
            timestamp="2025-01-01T00:00:00Z",
            run_id="r",
        )
        # (1 + 1 + 1 + (1 - 1)) / 4 = 0.75
        assert summary.overall_score == pytest.approx(0.75)

    def test_to_dict_contains_overall_score(self):
        report = self._make_report()
        summary = SystemEvaluationSummary.from_report(report)
        d = summary.to_dict()
        assert "overall_score" in d


# ---------------------------------------------------------------------------
# ComparativeEvaluationSummary
# ---------------------------------------------------------------------------


class TestComparativeEvaluationSummary:
    def _make_delta(self, net=0.12):
        return DeltaReport(
            run_id_a="a",
            run_id_b="b",
            config_a_name="baseline",
            config_b_name="candidate",
            timestamp="2025-01-01T00:00:00Z",
            metric_deltas={"precision@5": net, "recall@10": -0.02},
            scores_a={"precision@5": 0.7, "recall@10": 0.8},
            scores_b={"precision@5": 0.7 + net, "recall@10": 0.78},
        )

    def test_from_delta_recommend_promote(self):
        delta = self._make_delta(net=0.12)
        summary = ComparativeEvaluationSummary.from_delta_report(delta, "v1", "v2")
        assert summary.recommendation == "promote"

    def test_from_delta_recommend_reject(self):
        delta = self._make_delta(net=-0.10)
        summary = ComparativeEvaluationSummary.from_delta_report(delta, "v1", "v2")
        assert summary.recommendation == "reject"

    def test_improvements_and_regressions_split(self):
        delta = self._make_delta(net=0.12)
        summary = ComparativeEvaluationSummary.from_delta_report(delta, "v1", "v2")
        assert "precision@5" in summary.improvements
        assert "recall@10" in summary.regressions

    def test_to_dict_keys(self):
        delta = self._make_delta()
        summary = ComparativeEvaluationSummary.from_delta_report(delta, "v1", "v2")
        d = summary.to_dict()
        assert "net_delta" in d
        assert "recommendation" in d
