"""W5.P4 tests — PathRouter.route_with_features() feature-vector dispatch."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from agentic_core.L0_routing.reasoning.assembly_stage import GovernedPayload
from agentic_core.L0_routing.reasoning.path_router import (
    PathRouter,
    R5_ROUTE,
    RoutingFeatureDispatch,
)
from agentic_core.L6_observability.routing_calibration_metrics import (
    METRIC_R5_FIRED,
    reset_counters,
    snapshot_counters,
)
from agentic_core.runtime.contracts.routing_features import (
    NO_SIGNAL,
    RoutingFeatureVector,
    WorkClass,
    build_feature_vector,
)


@pytest.fixture(autouse=True)
def _reset_metrics() -> Iterator[None]:
    reset_counters()
    yield
    reset_counters()


def _payload() -> GovernedPayload:
    return GovernedPayload(
        s0_system="sys",
        i0_instructional="inst",
        c0_context="ctx",
        u0_user_prompt="user question",
        d0_injections="fence",
        check_ids=(),
        sanitized=True,
    )


def _fv(**overrides) -> RoutingFeatureVector:
    defaults = {
        "work_class": WorkClass.FACTUAL,
        "freshness_class": "bounded",
        "grounding_need_score": NO_SIGNAL,
        "ood_score": NO_SIGNAL,
        "budget_headroom_ratio": NO_SIGNAL,
    }
    defaults.update(overrides)
    return build_feature_vector(**defaults)


class TestR5MultiSignalDispatch:
    def test_toxicity_fires_r5(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(),
            toxicity_flagged=True,
        )
        assert result["gate_fired"] == "r5_multi_signal"
        assert result["result"]["route"] == R5_ROUTE
        assert result["r5_primary_reason"] == "r5_toxicity_flagged"

    def test_circuit_breaker_fires_r5(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(), _fv(), circuit_breaker_open=True,
        )
        assert result["gate_fired"] == "r5_multi_signal"
        assert result["r5_primary_reason"] == "r5_circuit_breaker_open"

    def test_budget_fires_r5(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(), _fv(), budget_exceeded=True,
        )
        assert result["gate_fired"] == "r5_multi_signal"
        assert result["r5_primary_reason"] == "r5_budget_exceeded"

    def test_ood_from_feature_vector_fires_r5(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(ood_score=0.85),  # above 0.70 default OOD threshold
        )
        assert result["gate_fired"] == "r5_multi_signal"
        assert result["r5_primary_reason"] == "r5_ood_detected"

    def test_low_confidence_fires_r5(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(), _fv(), confidence=0.30, threshold=0.50,
        )
        assert result["gate_fired"] == "r5_multi_signal"
        assert result["r5_primary_reason"] == "r5_low_confidence"

    def test_r5_metric_emitted_with_primary_reason(self) -> None:
        router = PathRouter()
        router.route_with_features(
            _payload(), _fv(), toxicity_flagged=True, namespace="rg",
        )
        snap = snapshot_counters()
        assert snap.get((METRIC_R5_FIRED, "rg", "r5_toxicity_flagged")) == 1


class TestR3GateDispatch:
    def test_high_grounding_need_fires_r3(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(grounding_need_score=0.85),  # above 0.70 default
        )
        assert result["gate_fired"] == "r3_gate"
        assert result["result"]["route"] == "R3"
        assert result["r3_reason_code"] == "d3_grounding_required"

    def test_grounding_required_with_low_coverage(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(grounding_need_score=0.90),
            coverage_score=0.30,  # below 0.60 default floor
        )
        assert result["gate_fired"] == "r3_gate"
        assert result["r3_reason_code"] == "d3_coverage_below_floor"

    def test_below_threshold_falls_through(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(grounding_need_score=0.20),  # below threshold
        )
        assert result["gate_fired"] == "fallback"

    def test_no_grounding_signal_falls_through(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(grounding_need_score=NO_SIGNAL),
        )
        assert result["gate_fired"] == "fallback"


class TestFallbackDispatch:
    def test_empty_signals_falls_back_to_route_with_confidence(self) -> None:
        router = PathRouter()
        result = router.route_with_features(
            _payload(),
            _fv(),  # no signals, default confidence=1.0
        )
        assert result["gate_fired"] == "fallback"
        # Falls through to confidence-aware selector — Path.B (sanitized=True).
        assert result["result"]["route"] in {"A", "B", "C", "D"}

    def test_fallback_preserves_existing_contract(self) -> None:
        router = PathRouter()
        result = router.route_with_features(_payload(), _fv())
        # RoutingResult shape preserved.
        for key in ("route", "reason", "confidence", "threshold", "action"):
            assert key in result["result"]


class TestRoutingFeatureDispatchShape:
    def test_return_type_is_typed_dict(self) -> None:
        router = PathRouter()
        result = router.route_with_features(_payload(), _fv())
        # TypedDict at runtime is just a dict.
        assert isinstance(result, dict)
        for key in (
            "result", "gate_fired", "r5_primary_reason",
            "r5_triggered_reasons", "r3_reason_code",
        ):
            assert key in result


class TestBackCompat:
    def test_route_with_confidence_still_works(self) -> None:
        router = PathRouter()
        # Existing API untouched.
        result = router.route_with_confidence(_payload(), 0.80, 0.50)
        assert result["route"] in {"A", "B", "C", "D"}

    def test_select_path_still_works(self) -> None:
        router = PathRouter()
        path = router.select_path(_payload())
        assert path.value in {"A", "B", "C", "D"}
