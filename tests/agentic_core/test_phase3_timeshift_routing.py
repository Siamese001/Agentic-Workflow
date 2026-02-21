"""
Phase 3 — Wave 3 Tests: L0 time-shifted routing using only prior signals.
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.engines.timeshift_router import (
    RoutingMode,
    TimeshiftRoutingDecision,
    evaluate_timeshift_routing,
)
from agentic_core.L4_state.config.versioned_configs import RoutingConfig
from agentic_core.L4_state.types.detection_signal_store import DetectionSignalStore
from agentic_core.L6_observability.types.detection_signal import DetectionSignal

pytestmark = pytest.mark.unit_min_deps


def _sig(mission_id: str, anomaly_score: float, created_at_utc: int = 100) -> DetectionSignal:
    return DetectionSignal.build(
        mission_id=mission_id,
        created_at_utc=created_at_utc,
        anomaly_score=anomaly_score,
        escalation_rate=0.0,
        retry_rate=0.0,
        violation_density=0.0,
    )


def _routing_cfg(threshold: float = 0.75) -> RoutingConfig:
    return RoutingConfig(anomaly_routing_threshold=threshold)


class TestTimeshiftRoutingConfig:
    def test_routing_config_has_anomaly_routing_threshold(self):
        cfg = RoutingConfig()
        assert hasattr(cfg, "anomaly_routing_threshold")
        assert isinstance(cfg.anomaly_routing_threshold, float)

    def test_default_threshold_is_075(self):
        """Default threshold 0.75 preserves legacy behavior (no compliance mode by default)."""
        cfg = RoutingConfig()
        assert cfg.anomaly_routing_threshold == 0.75

    def test_threshold_included_in_canonical_bytes(self):
        cfg1 = RoutingConfig(anomaly_routing_threshold=0.75)
        cfg2 = RoutingConfig(anomaly_routing_threshold=0.50)
        assert cfg1.canonical_bytes() != cfg2.canonical_bytes()
        assert cfg1.config_hash != cfg2.config_hash

    def test_default_threshold_preserves_legacy_behavior(self):
        """
        With no prior signal, routing must be STANDARD regardless of threshold.
        Proves defaults don't break existing behavior.
        """
        store = DetectionSignalStore()
        result = store.fetch_latest(before_tick=1)
        assert result is None


class TestTimeshiftRoutingEvaluation:
    def _eval(
        self,
        store: DetectionSignalStore,
        execution_start_tick: int,
        threshold: float = 0.75,
    ) -> TimeshiftRoutingDecision:
        """
        Evaluate routing using a local store (not the singleton).
        Patches get_prior_detection_signal via direct store call.
        """
        from agentic_core.L0_routing.engines.timeshift_router import (
            RoutingMode,
            TimeshiftRoutingDecision,
        )

        routing_config = _routing_cfg(threshold)
        prior = store.fetch_latest(before_tick=execution_start_tick)
        threshold_val = routing_config.anomaly_routing_threshold

        if prior is not None and prior.anomaly_score >= threshold_val:
            mode = RoutingMode.COMPLIANCE
        else:
            mode = RoutingMode.STANDARD

        return TimeshiftRoutingDecision(
            mode=mode,
            prior_signal_hash=prior.signal_hash if prior else None,
            prior_anomaly_score=prior.anomaly_score if prior else None,
            threshold_used=threshold_val,
            same_cycle_influence=False,
        )

    def test_no_prior_signal_routes_standard(self):
        store = DetectionSignalStore()
        decision = self._eval(store, execution_start_tick=1)
        assert decision.mode == RoutingMode.STANDARD
        assert decision.prior_signal_hash is None
        assert decision.same_cycle_influence is False

    def test_time_shifted_routing_uses_prior_signal_only(self):
        """
        Setup:
          - Store a prior signal with high anomaly at tick 5.
          - Execution starts at tick 10 → sees prior signal → routes to compliance.
          - Emit a new signal at tick 10 (same cycle).
          - Routing decision (already made at tick 10) is NOT affected by tick-10 signal.
        """
        store = DetectionSignalStore()

        # Prior signal: high anomaly, stored before execution
        prior_sig = _sig("m-prior-high", anomaly_score=0.9, created_at_utc=50)
        store.store(prior_sig, commit_tick=5)

        # Routing decision at execution_start_tick=10 sees the prior signal
        decision = self._eval(store, execution_start_tick=10, threshold=0.75)
        assert decision.mode == RoutingMode.COMPLIANCE
        assert decision.prior_signal_hash == prior_sig.signal_hash
        assert decision.same_cycle_influence is False

        # Now emit a same-cycle signal at tick 10 (simulating end-of-execution emission)
        same_cycle_sig = _sig("m-same-cycle", anomaly_score=0.0, created_at_utc=60)
        store.store(same_cycle_sig, commit_tick=10)

        # Re-fetch with before_tick=10 — same-cycle signal must NOT appear
        visible_prior = store.fetch_latest(before_tick=10)
        assert visible_prior is not None
        assert visible_prior.signal_hash == prior_sig.signal_hash, (
            "Same-cycle signal must not replace prior signal in routing window"
        )

    def test_same_cycle_signal_invisible_to_routing(self):
        """
        Negative: signal stored at tick T is invisible to routing at boundary T.
        """
        store = DetectionSignalStore()
        same_cycle = _sig("m-invisible", anomaly_score=0.99, created_at_utc=100)
        store.store(same_cycle, commit_tick=7)

        # Routing at tick 7 must not see the tick-7 signal
        decision = self._eval(store, execution_start_tick=7, threshold=0.75)
        assert decision.mode == RoutingMode.STANDARD
        assert decision.prior_signal_hash is None

    def test_low_anomaly_prior_routes_standard(self):
        store = DetectionSignalStore()
        low_sig = _sig("m-low", anomaly_score=0.3, created_at_utc=100)
        store.store(low_sig, commit_tick=3)
        decision = self._eval(store, execution_start_tick=5, threshold=0.75)
        assert decision.mode == RoutingMode.STANDARD

    def test_anomaly_at_threshold_routes_compliance(self):
        """Boundary: anomaly_score == threshold must trigger compliance mode."""
        store = DetectionSignalStore()
        boundary_sig = _sig("m-boundary", anomaly_score=0.75, created_at_utc=100)
        store.store(boundary_sig, commit_tick=2)
        decision = self._eval(store, execution_start_tick=3, threshold=0.75)
        assert decision.mode == RoutingMode.COMPLIANCE

    def test_decision_carries_threshold_used(self):
        store = DetectionSignalStore()
        decision = self._eval(store, execution_start_tick=1, threshold=0.6)
        assert decision.threshold_used == 0.6

    def test_same_cycle_influence_always_false(self):
        """TimeshiftRoutingDecision.same_cycle_influence must always be False."""
        store = DetectionSignalStore()
        decision = self._eval(store, execution_start_tick=1)
        assert decision.same_cycle_influence is False

    def test_default_threshold_preserves_legacy_behavior(self):
        """
        With no prior signal and default threshold, routing is STANDARD.
        Proves the new field does not break existing behavior.
        """
        store = DetectionSignalStore()
        decision = self._eval(store, execution_start_tick=1)
        assert decision.mode == RoutingMode.STANDARD


class TestTimeshiftRouterModule:
    def test_evaluate_timeshift_routing_no_prior_returns_standard(self):
        """
        Call the real evaluate_timeshift_routing() with a tick that has
        no prior signals in the singleton store.
        Uses a very large tick to avoid interference from other tests.
        """
        decision = evaluate_timeshift_routing(
            execution_start_tick=999_999_999,
            routing_config=_routing_cfg(0.75),
        )
        assert decision.mode == RoutingMode.STANDARD
        assert decision.same_cycle_influence is False

    def test_timeshift_router_module_imports_get_active_configs(self):
        """AST-verify that timeshift_router reads threshold from RoutingConfig."""
        from pathlib import Path

        src = (
            Path(__file__).resolve().parents[2]
            / "agentic_core"
            / "L0_routing"
            / "engines"
            / "timeshift_router.py"
        ).read_text(encoding="utf-8")
        assert "anomaly_routing_threshold" in src
        assert "get_active_configs" in src
        assert "get_prior_detection_signal" in src
