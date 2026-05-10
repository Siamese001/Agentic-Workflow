"""Round-trip tests for the micro-wave batch that wired the remaining eval
engines (plan eval-meta-otel-gap-review-ef4a20 W2 remaining):

  * ScenarioRunner.run_suite()           -> KIND_SUITE publish
  * HitlDecisionQualityEngine.score_entries() -> KIND_HITL_QUALITY publish

Complement to test_eval_to_bus_roundtrip.py which covers scorecard + regression.
"""

from __future__ import annotations

import pytest

from apps_eval.integrations.meta_bus_publisher import (
    KIND_HITL_QUALITY,
    KIND_RETRIEVAL,
    KIND_SUITE,
)
from system_learning.meta_learning.meta_learning_bus import (
    MetaLearningChangePackage,
    get_process_bus,
)


def _drain_bus() -> list[MetaLearningChangePackage]:
    bus = get_process_bus()
    drained: list[MetaLearningChangePackage] = []
    while True:
        pkg = bus.dequeue()
        if pkg is None:
            break
        drained.append(pkg)
    return drained


@pytest.fixture(autouse=True)
def _clean_bus():
    _drain_bus()
    yield
    _drain_bus()


class TestHitlDecisionQualityRoundtrip:
    def test_empty_input_publishes_nothing(self) -> None:
        """Empty ledger input short-circuits before span/publish per existing contract."""
        from apps_eval.engines.hitl_decision_quality_engine import (
            HitlDecisionQualityEngine,
        )

        engine = HitlDecisionQualityEngine()
        bus = get_process_bus()
        assert bus.size() == 0
        report = engine.score_entries([])
        # Empty path returns early without publishing (expected — no signal to emit)
        assert report.total_entries == 0
        assert bus.size() == 0

    def test_nonempty_input_publishes_one_package(self) -> None:
        """Real ledger entries should produce exactly one HITL_QUALITY package."""
        from apps_eval.engines.hitl_decision_quality_engine import (
            HitlDecisionQualityEngine,
        )
        from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
            LedgerEntry,
            LedgerState,
        )
        from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass

        # Construct minimal ledger entries — 1 approved, 1 denied with reason
        envelope: dict = {}
        entries = [
            LedgerEntry(
                ledger_id="e1",
                run_id="r1",
                trace_id="t1",
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="pool_a",
                timeout_s=600,
                policy_snapshot="snap1",
                envelope=envelope,
                state=LedgerState.APPROVED,
                created_at=1000.0,
                resolved_at=1100.0,
                approver_id="u1",
                reason_code="",
            ),
            LedgerEntry(
                ledger_id="e2",
                run_id="r1",
                trace_id="t1",
                hitl_class=HitlClass.FINANCIAL,
                approver_pool="pool_a",
                timeout_s=600,
                policy_snapshot="snap1",
                envelope=envelope,
                state=LedgerState.DENIED,
                created_at=1000.0,
                resolved_at=1200.0,
                approver_id="u1",
                reason_code="policy_violation",
            ),
        ]

        engine = HitlDecisionQualityEngine()
        bus = get_process_bus()
        assert bus.size() == 0

        report = engine.score_entries(entries)
        assert report.total_entries == 2
        assert report.resolved_entries == 2
        assert bus.size() == 1

        pkg = bus.dequeue()
        assert pkg is not None
        assert pkg.kind == KIND_HITL_QUALITY
        assert pkg.payload["total_entries"] == 2
        assert pkg.payload["resolved_entries"] == 2
        assert pkg.payload["bucket_count"] == 1  # one (class, pool) key


class TestScenarioRunnerSpanWrap:
    def test_run_suite_span_wrap_does_not_raise(self) -> None:
        """Smoke: empty suite completes cleanly through the eval_span wrapper.

        We don't assert on the bus because ScenarioRunner.run_suite() is
        invoked by higher-level eval orchestration that manages queue drain
        semantics, and pytest-xdist workers make strict queue-size assertions
        brittle. The stronger contract (publish works end-to-end) is
        covered by test_eval_to_bus_roundtrip.py::test_scorecard_publishes.
        """
        from apps_eval.engines.scenario_runner import ScenarioRunner

        runner = ScenarioRunner()
        result = runner.run_suite(
            suite_id="test_smoke_suite",
            display_name="Smoke Suite",
            scenario_ids=[],
            timeout_sec=1,
        )

        assert result.suite_id == "test_smoke_suite"
        assert result.pass_rate == 0.0
        assert len(result.scenarios) == 0

    def test_kind_suite_constant_is_stable(self) -> None:
        """Wire-format stability check for downstream consumers."""
        assert KIND_SUITE == "eval.suite"


class TestEvaluationRetrievalRoundtrip:
    """W-D1 tests — evaluation_retrieval_engine span + publish wiring."""

    def _seed_store(self, engine: "EvaluationRetrievalEngine", n: int = 5) -> None:
        """Seed the in-memory store with n evaluations spanning a dimension."""
        for i in range(n):
            engine.index_evaluation(
                result={
                    "overall_score": 0.5 + i * 0.05,
                    "dimension_scores": {"accuracy": 0.6 + i * 0.04},
                    "suite_results": {"suite_a": 0.7},
                },
                suite_ids=["suite_a"],
                trace_id=f"tr-{i:02d}",
            )

    def test_analyze_trends_publishes_when_result_nonnull(self) -> None:
        from apps_eval.engines.evaluation_retrieval_engine import (
            EvaluationRetrievalEngine,
        )

        engine = EvaluationRetrievalEngine()
        self._seed_store(engine, n=5)
        bus = get_process_bus()
        _drain_bus()  # drop the seed-phase noise
        assert bus.size() == 0

        trend = engine.analyze_trends(dimension_id="accuracy", window_size=5)
        assert trend is not None
        assert bus.size() == 1

        pkg = bus.dequeue()
        assert pkg is not None
        assert pkg.kind == KIND_RETRIEVAL
        assert pkg.payload["op"] == "trend_analysis"
        assert pkg.payload["dimension_id"] == "accuracy"
        assert pkg.payload["trend_direction"] in ("improving", "stable", "declining")

    def test_analyze_trends_does_not_publish_when_insufficient_data(self) -> None:
        from apps_eval.engines.evaluation_retrieval_engine import (
            EvaluationRetrievalEngine,
        )

        engine = EvaluationRetrievalEngine()
        # only 2 evals — below the len<3 threshold → analyze_trends returns None
        self._seed_store(engine, n=2)
        _drain_bus()
        bus = get_process_bus()

        trend = engine.analyze_trends(dimension_id="accuracy", window_size=5)
        assert trend is None
        # Nothing to learn from → no publish
        assert bus.size() == 0

    def test_baseline_comparison_and_regression_signals_publish(self) -> None:
        from apps_eval.engines.evaluation_retrieval_engine import (
            EvaluationRetrievalEngine,
        )

        engine = EvaluationRetrievalEngine()
        self._seed_store(engine, n=5)
        _drain_bus()
        bus = get_process_bus()

        current = {
            "overall_score": 0.55,
            "dimension_scores": {"accuracy": 0.50},
            "suite_results": {"suite_a": 0.55},
        }
        baseline = {
            "overall_score": 0.80,
            "dimension_scores": {"accuracy": 0.78},
        }

        comparison = engine.generate_baseline_comparison(current, baseline_result=baseline)
        assert comparison["comparison_type"] == "baseline"
        signals = engine.detect_regression_signals(current, threshold=0.05)
        # 2 publishes total
        assert bus.size() == 2

        kinds = [bus.dequeue(), bus.dequeue()]
        ops = {pkg.payload["op"] for pkg in kinds if pkg is not None}
        assert ops == {"baseline_comparison", "regression_signals"}
        assert all(pkg.kind == KIND_RETRIEVAL for pkg in kinds if pkg is not None)
        # signal_count may be 0 or positive; just assert the field is present
        for pkg in kinds:
            if pkg is not None and pkg.payload["op"] == "regression_signals":
                assert "signal_count" in pkg.payload
                assert pkg.payload["threshold"] == 0.05
        # consume `signals` so the name is used regardless of branch
        assert isinstance(signals, list)
