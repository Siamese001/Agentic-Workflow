"""W1.P3 unit tests — feature_vector pass-through via RoutingTelemetry.

These tests verify the additive wiring is back-compat:
    (a) Existing callers (no feature_vector) continue to work unchanged.
    (b) When a feature vector IS supplied, it reaches the persisted record
        without mutation.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from agentic_core.L0_routing.utils.routing_telemetry import (
    RoutingOutcomeStatus,
    RoutingTelemetryContext,
    get_routing_telemetry_store,
    record_routing_telemetry,
    reset_routing_telemetry_store,
)
from agentic_core.runtime.contracts.routing_features import (
    WorkClass,
    build_feature_vector,
)


@pytest.fixture(autouse=True)
def _reset_store() -> Iterator[None]:
    reset_routing_telemetry_store()
    yield
    reset_routing_telemetry_store()


def _minimal_ctx(
    feature_vector=None,
) -> RoutingTelemetryContext:
    return RoutingTelemetryContext(
        router_id="test-router",
        routing_contract_id="contract-abc",
        request_hash="hash-xyz",
        candidate_routes=["R1A", "R1B", "R3", "R5"],
        chosen_route="R3",
        outcome=RoutingOutcomeStatus.ROUTE_SUCCEEDED,
        run_id="run-1",
        trace_id="trace-1",
        routing_start_tick=100.0,
        routing_end_tick=100.5,
        feature_vector=feature_vector,
    )


class TestBackCompat:
    def test_context_accepts_no_feature_vector(self) -> None:
        # Existing callers never pass feature_vector. This MUST still work.
        ctx = RoutingTelemetryContext(
            router_id="legacy",
            routing_contract_id="c",
            request_hash="h",
            candidate_routes=["A", "B"],
            chosen_route="A",
            outcome=RoutingOutcomeStatus.ROUTE_SUCCEEDED,
        )
        assert ctx.feature_vector is None

    def test_record_without_feature_vector_succeeds(self) -> None:
        ctx = _minimal_ctx(feature_vector=None)
        record = record_routing_telemetry(ctx)
        assert record.feature_vector is None

    def test_store_back_compat_query_paths(self) -> None:
        ctx = _minimal_ctx(feature_vector=None)
        record_routing_telemetry(ctx)
        store = get_routing_telemetry_store()
        assert len(store.by_run_id("run-1")) == 1
        assert len(store.by_trace_id("trace-1")) == 1


class TestFeatureVectorPassthrough:
    def test_feature_vector_reaches_persisted_record(self) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
            ood_score=0.10,
            budget_headroom_ratio=0.45,
        )
        ctx = _minimal_ctx(feature_vector=fv)
        record = record_routing_telemetry(ctx)
        assert record.feature_vector is not None
        assert record.feature_vector.manifest_hash == fv.manifest_hash
        assert record.feature_vector.work_class is WorkClass.FACTUAL
        assert record.feature_vector.grounding_need_score == pytest.approx(0.82)

    def test_feature_vector_immutable_across_passthrough(self) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.COMPARE,
            grounding_need_score=0.75,
        )
        record = record_routing_telemetry(_minimal_ctx(feature_vector=fv))
        # Same instance (dataclass is frozen — identity is fine).
        assert record.feature_vector is fv

    def test_feature_vector_log_line_emitted(self, caplog: pytest.LogCaptureFixture) -> None:
        fv = build_feature_vector(
            work_class=WorkClass.FACTUAL,
            freshness_class="fresh",
            grounding_need_score=0.82,
        )
        caplog.set_level(
            "DEBUG",
            logger="agentic_core.L0_routing.utils.routing_telemetry",
        )
        record_routing_telemetry(_minimal_ctx(feature_vector=fv))
        feature_lines = [r for r in caplog.records if "ROUTING_FEATURE_VECTOR" in r.getMessage()]
        assert len(feature_lines) == 1, (
            f"Expected exactly one ROUTING_FEATURE_VECTOR log line (got {len(feature_lines)})"
        )

    def test_no_log_line_when_no_feature_vector(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(
            "DEBUG",
            logger="agentic_core.L0_routing.utils.routing_telemetry",
        )
        record_routing_telemetry(_minimal_ctx(feature_vector=None))
        feature_lines = [r for r in caplog.records if "ROUTING_FEATURE_VECTOR" in r.getMessage()]
        assert len(feature_lines) == 0
