"""W4.P1 tests — routing calibration OTEL metric emitters."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from agentic_core.L6_observability.routing_calibration_metrics import (
    METRIC_R1_EXACT_HIT,
    METRIC_R1_SEMANTIC_HIT,
    METRIC_R3_COVERAGE_BELOW_FLOOR,
    METRIC_R3_GROUNDED,
    METRIC_R5_FIRED,
    hit_ratio,
    record_r1_exact_hit,
    record_r1_semantic_hit,
    record_r3_coverage_below_floor,
    record_r3_grounded,
    record_r5_fired,
    reset_counters,
    snapshot_counters,
)


@pytest.fixture(autouse=True)
def _reset() -> Iterator[None]:
    reset_counters()
    yield
    reset_counters()


class TestFallbackCounters:
    def test_r1_exact_hit_counter_increments(self) -> None:
        record_r1_exact_hit("rg")
        record_r1_exact_hit("rg")
        snap = snapshot_counters()
        assert snap[(METRIC_R1_EXACT_HIT, "rg", "")] == 2

    def test_r1_semantic_hit_counter_increments(self) -> None:
        record_r1_semantic_hit("research", increment=3)
        snap = snapshot_counters()
        assert snap[(METRIC_R1_SEMANTIC_HIT, "research", "")] == 3

    def test_r5_fired_labels_by_reason_code(self) -> None:
        record_r5_fired("r5_low_confidence", namespace="rg")
        record_r5_fired("r5_ood_detected", namespace="rg")
        record_r5_fired("r5_low_confidence", namespace="rg")
        snap = snapshot_counters()
        assert snap[(METRIC_R5_FIRED, "rg", "r5_low_confidence")] == 2
        assert snap[(METRIC_R5_FIRED, "rg", "r5_ood_detected")] == 1

    def test_r3_coverage_below_floor_counter(self) -> None:
        record_r3_coverage_below_floor("eval")
        snap = snapshot_counters()
        assert snap[(METRIC_R3_COVERAGE_BELOW_FLOOR, "eval", "")] == 1

    def test_r3_grounded_counter(self) -> None:
        record_r3_grounded("rg", increment=5)
        snap = snapshot_counters()
        assert snap[(METRIC_R3_GROUNDED, "rg", "")] == 5

    def test_default_namespace_is_default(self) -> None:
        record_r1_exact_hit()
        snap = snapshot_counters()
        assert snap[(METRIC_R1_EXACT_HIT, "default", "")] == 1

    def test_zero_increment_is_noop(self) -> None:
        record_r1_exact_hit("rg", increment=0)
        assert snapshot_counters() == {}

    def test_negative_increment_is_noop(self) -> None:
        record_r1_exact_hit("rg", increment=-5)
        assert snapshot_counters() == {}


class TestHitRatio:
    def test_hit_ratio_empty_returns_zero(self) -> None:
        assert hit_ratio("rg") == 0.0

    def test_hit_ratio_all_hits_returns_one(self) -> None:
        record_r1_exact_hit("rg")
        record_r1_semantic_hit("rg")
        assert hit_ratio("rg") == pytest.approx(1.0)

    def test_hit_ratio_mixed(self) -> None:
        # 3 hits, 1 R5 = 3/4 = 0.75
        record_r1_exact_hit("rg", increment=2)
        record_r1_semantic_hit("rg")
        record_r5_fired("r5_low_confidence", namespace="rg")
        assert hit_ratio("rg") == pytest.approx(0.75)

    def test_hit_ratio_all_r5_returns_zero(self) -> None:
        record_r5_fired("r5_low_confidence", namespace="rg", increment=5)
        assert hit_ratio("rg") == pytest.approx(0.0)

    def test_hit_ratio_namespace_isolation(self) -> None:
        record_r1_exact_hit("rg")
        record_r5_fired("r5_low_confidence", namespace="eval")
        # rg: 1 hit, 0 r5 = 1.0. eval: 0 hits, 1 r5 = 0.0.
        assert hit_ratio("rg") == pytest.approx(1.0)
        assert hit_ratio("eval") == pytest.approx(0.0)


class TestResetCounters:
    def test_reset_clears_all_state(self) -> None:
        record_r1_exact_hit("rg")
        record_r1_semantic_hit("eval")
        record_r5_fired("r5_low_confidence", namespace="rg")
        reset_counters()
        assert snapshot_counters() == {}
        assert hit_ratio("rg") == 0.0
