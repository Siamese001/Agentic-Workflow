"""ADG-driven tests for evaluation/metrics/base.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_base_adg")
_emit_applies_guardrail("p0", "test_base_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_base_adg", "policy_binding")
_emit_snapshots_state("p0", "test_base_adg", "state_snapshot")
emit_replay_key("p0", "test_base_adg")
emit_determinism_digest("p0", "test_base_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.evaluation.metrics.base import EvaluationMetric, RetrievalMetric


class TestEvaluationMetric:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(EvaluationMetric)

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            EvaluationMetric()

    def test_subclass_requires_name_and_compute(self):
        class Concrete(EvaluationMetric):
            @property
            def name(self) -> str:
                return "test"

            def compute(self, prediction, ground_truth, context=None) -> float:
                return 1.0

        m = Concrete()
        assert m.name == "test"
        assert m.compute("a", "b") == pytest.approx(1.0)


class TestRetrievalMetric:
    def test_is_abstract(self):
        import inspect
        assert inspect.isabstract(RetrievalMetric)

    def test_is_subclass_of_evaluation_metric(self):
        assert issubclass(RetrievalMetric, EvaluationMetric)
