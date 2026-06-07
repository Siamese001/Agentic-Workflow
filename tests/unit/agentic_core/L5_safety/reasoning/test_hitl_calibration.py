"""Unit tests for ``agentic_core.L5_safety.reasoning.hitl_calibration``.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` W9.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.reasoning.hitl_calibration import (
    AdversarialProbeSuite,
    HITLCalibrationLedger,
)


def test_hitl_ledger_empty_fp_rate_zero() -> None:
    ledger = HITLCalibrationLedger()
    assert ledger.false_positive_rate() == 0.0


def test_hitl_ledger_instant_approvals_dominate_fp_rate() -> None:
    ledger = HITLCalibrationLedger()
    for i in range(80):
        ledger.record(
            decision_id=f"d_{i}",
            fired_reason="toxicity_flagged",
            approved=True,
            latency_seconds=2.0,  # within threshold
        )
    for i in range(20):
        ledger.record(
            decision_id=f"d_{i+80}",
            fired_reason="toxicity_flagged",
            approved=False,
            latency_seconds=120.0,  # genuine review
        )
    assert ledger.false_positive_rate(instant_threshold_seconds=5.0) == pytest.approx(0.80)


def test_hitl_ledger_slow_approvals_not_fp() -> None:
    ledger = HITLCalibrationLedger()
    for i in range(50):
        ledger.record(
            decision_id=f"d_{i}",
            fired_reason="ambiguous",
            approved=True,
            latency_seconds=60.0,  # genuine review
        )
    assert ledger.false_positive_rate(instant_threshold_seconds=5.0) == 0.0


def test_hitl_ledger_per_reason_isolation() -> None:
    ledger = HITLCalibrationLedger()
    # toxicity: 100% instant-approved
    for i in range(20):
        ledger.record(
            decision_id=f"tx_{i}",
            fired_reason="toxicity",
            approved=True,
            latency_seconds=1.0,
        )
    # ambiguity: 0% instant-approved
    for i in range(20):
        ledger.record(
            decision_id=f"amb_{i}",
            fired_reason="ambiguity",
            approved=True,
            latency_seconds=60.0,
        )
    rates = ledger.per_reason_fp_rate(instant_threshold_seconds=5.0)
    assert rates["toxicity"] == pytest.approx(1.0)
    assert rates["ambiguity"] == pytest.approx(0.0)


def test_hitl_ledger_negative_latency_raises() -> None:
    ledger = HITLCalibrationLedger()
    with pytest.raises(ValueError):
        ledger.record(
            decision_id="d",
            fired_reason="r",
            approved=True,
            latency_seconds=-1.0,
        )


def test_hitl_event_bucket_assignment() -> None:
    ledger = HITLCalibrationLedger()
    ledger.record(decision_id="d1", fired_reason="r", approved=True, latency_seconds=2.0)
    ledger.record(decision_id="d2", fired_reason="r", approved=True, latency_seconds=100.0)
    ledger.record(decision_id="d3", fired_reason="r", approved=True, latency_seconds=10000.0)
    snap = ledger.snapshot()
    assert snap[0].bucket == "<= 5s"
    assert snap[1].bucket == "<= 120s"
    assert snap[2].bucket == "> 600s"


def test_probe_suite_escape_rate_zero_when_empty() -> None:
    suite = AdversarialProbeSuite()
    assert suite.escape_rate() == 0.0


def test_probe_suite_unregistered_record_raises() -> None:
    suite = AdversarialProbeSuite()
    with pytest.raises(KeyError):
        suite.record_outcome("probe_a", passed=True)


def test_probe_suite_register_empty_id_raises() -> None:
    suite = AdversarialProbeSuite()
    with pytest.raises(ValueError):
        suite.register_probe("")


def test_probe_suite_escape_rate_tracks_failures() -> None:
    suite = AdversarialProbeSuite()
    for i in range(10):
        suite.register_probe(f"probe_{i}")
    # 3 fail, 7 pass
    for i in range(3):
        suite.record_outcome(f"probe_{i}", passed=False, notes="regressed")
    for i in range(3, 10):
        suite.record_outcome(f"probe_{i}", passed=True)
    assert suite.escape_rate() == pytest.approx(0.30)
    escaped = suite.escaped_probes()
    assert escaped == {"probe_0", "probe_1", "probe_2"}


def test_probe_suite_unrun_probe_counts_as_passing() -> None:
    """A probe that has never been run cannot be in escape state."""
    suite = AdversarialProbeSuite()
    suite.register_probe("untested")
    suite.register_probe("tested_failing")
    suite.record_outcome("tested_failing", passed=False)
    # 1 escape out of 2 → 0.5
    assert suite.escape_rate() == 0.5


def test_probe_suite_latest_outcome_overrides_previous() -> None:
    suite = AdversarialProbeSuite()
    suite.register_probe("p")
    suite.record_outcome("p", passed=False)
    suite.record_outcome("p", passed=True)  # fixed
    assert suite.escape_rate() == 0.0
