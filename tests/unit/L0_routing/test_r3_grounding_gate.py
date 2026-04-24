"""W3.P1 tests — R3 grounded-read gate."""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest

from agentic_core.L0_routing.reasoning.route_gates import check_r3_grounding_gate
from agentic_core.runtime.config.routing_thresholds import (
    reload_routing_thresholds,
    set_config_path_for_testing,
)
from agentic_core.runtime.contracts.routing_features import NO_SIGNAL


@pytest.fixture(autouse=True)
def _clean_env() -> Iterator[None]:
    saved = {k: v for k, v in os.environ.items() if k.startswith("ROUTING_THRESHOLD__")}
    for k in list(os.environ):
        if k.startswith("ROUTING_THRESHOLD__"):
            del os.environ[k]
    set_config_path_for_testing(None)
    reload_routing_thresholds()
    yield
    for k in list(os.environ):
        if k.startswith("ROUTING_THRESHOLD__"):
            del os.environ[k]
    os.environ.update(saved)
    set_config_path_for_testing(None)
    reload_routing_thresholds()


class TestGroundingGate:
    def test_no_signal_returns_false(self) -> None:
        should, reason = check_r3_grounding_gate(NO_SIGNAL)
        assert should is False
        assert reason == "no_grounding_signal"

    def test_below_threshold_skips_r3(self) -> None:
        # Default threshold is 0.70.
        should, reason = check_r3_grounding_gate(0.50, threshold_override=0.70)
        assert should is False
        assert reason == "below_grounding_threshold"

    def test_at_threshold_selects_r3(self) -> None:
        should, reason = check_r3_grounding_gate(0.70, threshold_override=0.70)
        assert should is True
        assert reason == "d3_grounding_required"

    def test_above_threshold_selects_r3(self) -> None:
        should, reason = check_r3_grounding_gate(0.95, threshold_override=0.70)
        assert should is True
        assert reason == "d3_grounding_required"

    def test_coverage_below_floor_signals_broaden(self) -> None:
        # Grounding need is high, but post-C0 coverage is too weak.
        should, reason = check_r3_grounding_gate(
            0.90,
            coverage_score=0.30,
            threshold_override=0.70,
            coverage_floor_override=0.60,
        )
        assert should is True
        assert reason == "d3_coverage_below_floor"

    def test_coverage_above_floor_proceeds_normally(self) -> None:
        should, reason = check_r3_grounding_gate(
            0.90,
            coverage_score=0.80,
            threshold_override=0.70,
            coverage_floor_override=0.60,
        )
        assert should is True
        assert reason == "d3_grounding_required"

    def test_invalid_score_treated_as_no_signal(self) -> None:
        should, reason = check_r3_grounding_gate(1.5)
        assert should is False
        assert reason == "no_grounding_signal"

    def test_negative_score_treated_as_no_signal(self) -> None:
        # -1.0 happens to equal NO_SIGNAL; but -0.5 does not — both should
        # end up as no_grounding_signal to be safe.
        should, reason = check_r3_grounding_gate(-0.5)
        assert should is False
        assert reason == "no_grounding_signal"


class TestNamespaceThreshold:
    def test_namespace_lookup_used_when_override_absent(self) -> None:
        # underwriting_ai YAML override sets r3_grounding_need = 0.60.
        # Without threshold_override, the namespace lookup should apply.
        should, reason = check_r3_grounding_gate(
            0.65, namespace="underwriting_ai",
        )
        assert should is True  # 0.65 >= 0.60 for underwriting_ai
        assert reason == "d3_grounding_required"

    def test_namespace_without_override_uses_default(self) -> None:
        # "research" namespace has no r3_grounding_need override; falls back
        # to default 0.70.
        should, reason = check_r3_grounding_gate(
            0.65, namespace="research",
        )
        assert should is False  # 0.65 < 0.70 default
        assert reason == "below_grounding_threshold"

    def test_env_override_wins_over_namespace(self) -> None:
        os.environ["ROUTING_THRESHOLD__R3_GROUNDING_NEED"] = "0.30"
        reload_routing_thresholds()
        # Very permissive threshold via env → 0.65 clears it.
        should, reason = check_r3_grounding_gate(
            0.65, namespace="underwriting_ai",
        )
        assert should is True
        assert reason == "d3_grounding_required"
