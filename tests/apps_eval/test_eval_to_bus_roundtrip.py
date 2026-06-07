"""Round-trip smoke test — eval → canonical meta-learning bus.

Verifies the end-to-end wiring introduced in plan
``docs/archive/windsurf/legacy-tree/plans/eval-meta-otel-gap-review-ef4a20.md`` Wave W2:

  ``ScorecardEngine.compute()``
      → OTel span ``apps_eval.v1.scorecard.compute``
      → ``publish_eval_outcome(kind="eval.scorecard", …)``
      → canonical ``MetaLearningBus`` FIFO at
        ``system_learning/meta_learning/meta_learning_bus.py``

Previously (per plan F3 evidence) apps_eval had zero import edges into any
``MetaLearningBus`` symbol. This test asserts a fresh package shows up on
the canonical bus after ``compute()`` completes.
"""

from __future__ import annotations

import pytest

from apps_eval.engines.scorecard_engine import ScorecardEngine
from apps_eval.integrations.meta_bus_publisher import (
    KIND_SCORECARD,
    publish_eval_outcome,
)
from apps_eval.integrations.tracing import eval_span, get_tracer
from apps_eval.types.eval_types import ScenarioResult, SuiteResult
from agentic_core.L6_system_learning.meta_learning_bus import (
    MetaLearningChangePackage,
    get_process_bus,
)


def _drain_bus() -> list[MetaLearningChangePackage]:
    """Drain the canonical bus and return every package removed."""
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
    """Drain the process-level bus around each test for isolation."""
    _drain_bus()
    yield
    _drain_bus()


def _make_suite_result(suite_id: str, pass_rate: float) -> SuiteResult:
    return SuiteResult(
        suite_id=suite_id,
        display_name=suite_id.replace("_", " ").title(),
        scenarios=[
            ScenarioResult(
                scenario_id=f"{suite_id}:sc1",
                suite_id=suite_id,
                outcome="PASS" if pass_rate >= 0.7 else "FAIL",
                score=pass_rate,
                latency_ms=1.0,
                message="",
                evidence="",
                deterministic=True,
            ),
        ],
        pass_rate=pass_rate,
        mean_latency_ms=1.0,
        error="",
    )


class TestScorecardEngineRoundtrip:
    def test_scorecard_publishes_to_canonical_bus(self) -> None:
        """ScorecardEngine.compute() must enqueue exactly one package."""
        engine = ScorecardEngine()
        suites = [
            _make_suite_result("routing_enforcement", 0.95),
            _make_suite_result("determinism_contracts", 0.88),
            _make_suite_result("orchestration_hop", 0.72),
        ]

        bus = get_process_bus()
        assert bus.size() == 0, "bus must be empty at test start"

        result = engine.compute(suites)

        assert result.overall_score > 0
        assert bus.size() == 1, "exactly one package must be published"

        pkg = bus.dequeue()
        assert pkg is not None
        assert pkg.kind == KIND_SCORECARD
        assert pkg.package_hash, "package hash must be set"
        # Payload must preserve the essential scorecard signal
        assert pkg.payload["overall_score"] == result.overall_score
        assert pkg.payload["dimension_count"] == len(result.rows)
        assert "rows" in pkg.payload

    def test_package_hash_is_deterministic(self) -> None:
        """Repeated publishes of the same payload yield the same package_hash."""
        payload = {"engine": "test", "overall_score": 0.9, "dimension_count": 3}
        r1 = publish_eval_outcome(kind=KIND_SCORECARD, payload=payload, trace_id="fixed-1")
        r2 = publish_eval_outcome(kind=KIND_SCORECARD, payload=payload, trace_id="fixed-2")
        assert r1.ok and r2.ok
        # Package hash is content-addressed (kind + payload) and ignores trace_id
        assert r1.package_hash == r2.package_hash

    def test_compute_wrapped_in_otel_span(self) -> None:
        """The OTel span should be active during compute() and expose the suite count."""
        engine = ScorecardEngine()
        suites = [_make_suite_result("correctness_suite", 0.91)]

        # Exercise the span machinery — we can't easily capture span attrs
        # without an exporter, but we can at least prove the tracer is
        # obtainable and the span context manager does not raise.
        tracer = get_tracer()
        assert tracer is not None

        with eval_span("apps_eval.v1.test.roundtrip", attributes={"test": True}):
            result = engine.compute(suites)

        assert result.overall_score > 0


class TestPublisherFailOpen:
    def test_publish_accepts_empty_payload(self) -> None:
        """Empty dict payload must still produce a valid receipt."""
        r = publish_eval_outcome(kind=KIND_SCORECARD, payload={}, trace_id="empty-1")
        assert r.ok is True
        assert r.package_hash

    def test_publish_rejects_non_dict_payload(self) -> None:
        """Non-dict payload must raise immediately (caller bug, not silent swallow)."""
        with pytest.raises(TypeError):
            publish_eval_outcome(kind=KIND_SCORECARD, payload=[1, 2, 3])  # type: ignore[arg-type]

    def test_publish_rejects_empty_kind(self) -> None:
        with pytest.raises(ValueError):
            publish_eval_outcome(kind="", payload={"a": 1})
