"""Verify system_learning sub-modules are wired and deterministic."""

import pytest

pytestmark = pytest.mark.unit_min_deps

from system_learning.engines.arbitration.engine import ArbitrationEngine
from system_learning.engines.arbitration.types import (
    ArbitrationCandidate,
    ArbitrationPolicy,
)
from system_learning.engines.confidence.engine import HealingConfidenceScorer
from system_learning.engines.confidence.types import HealingAttempt
from system_learning.engines.correlation.engine import RiskCorrelator
from system_learning.engines.fingerprinting.engine import FailureFingerprinter
from system_learning.engines.fingerprinting.types import FailureEvent


def test_failure_fingerprinter_produces_deterministic_output():
    fp = FailureFingerprinter()
    event = FailureEvent(
        exc_type="ValueError", error_code="VAL_ERR", component="L2.executor", symbols=["execute"], metadata={}
    )
    f1 = fp.fingerprint(event)
    f2 = fp.fingerprint(event)
    assert f1.fingerprint_hex == f2.fingerprint_hex
    assert len(f1.fingerprint_hex) == 64


def test_failure_fingerprinter_different_events_differ():
    fp = FailureFingerprinter()
    e1 = FailureEvent(exc_type="ValueError", error_code="V1", component="A", symbols=[], metadata={})
    e2 = FailureEvent(exc_type="RuntimeError", error_code="V2", component="B", symbols=[], metadata={})
    assert fp.fingerprint(e1).fingerprint_hex != fp.fingerprint(e2).fingerprint_hex


def test_healing_confidence_scorer_maps_success_to_accept():
    scorer = HealingConfidenceScorer()
    attempt = HealingAttempt(attempt_id="a1", outcome="SUCCESS", severity=1, cost=1.0)
    report = scorer.score([attempt])
    assert len(report.decisions) == 1
    assert report.decisions[0].action == "ACCEPT"
    assert report.decisions[0].confidence == 1.0


def test_healing_confidence_scorer_maps_failure_to_reject():
    scorer = HealingConfidenceScorer()
    attempt = HealingAttempt(attempt_id="a2", outcome="FAILURE", severity=3, cost=2.0)
    report = scorer.score([attempt])
    assert report.decisions[0].action == "REJECT"
    assert report.decisions[0].confidence == 0.0


def test_healing_confidence_scorer_maps_partial_to_escalate():
    scorer = HealingConfidenceScorer()
    attempt = HealingAttempt(attempt_id="a3", outcome="PARTIAL", severity=2, cost=1.0)
    report = scorer.score([attempt])
    assert report.decisions[0].action == "ESCALATE"


def test_risk_correlator_deterministic():
    correlator = RiskCorrelator()
    report1 = correlator.build([], [])
    report2 = correlator.build([], [])
    assert report1.canonical_bytes == report2.canonical_bytes


def test_risk_correlator_different_inputs_differ():
    correlator = RiskCorrelator()
    r1 = correlator.build(["fp1", "fp2"], ["drift_a"])
    r2 = correlator.build(["fp3"], [])
    assert r1.canonical_bytes != r2.canonical_bytes


def test_arbitration_engine_selects_highest_score():
    engine = ArbitrationEngine()
    policy = ArbitrationPolicy(max_winners=1, min_score=0.0)
    candidates = [
        ArbitrationCandidate(id="c1", score=0.9, cost=1.0, kind="l0", payload={}),
        ArbitrationCandidate(id="c2", score=0.5, cost=1.0, kind="l0", payload={}),
    ]
    decision = engine.arbitrate(candidates, policy)
    assert decision.winner_ids == ["c1"]


def test_arbitration_engine_filters_below_min_score():
    engine = ArbitrationEngine()
    policy = ArbitrationPolicy(max_winners=3, min_score=0.7)
    candidates = [
        ArbitrationCandidate(id="c1", score=0.9, cost=1.0, kind="l0", payload={}),
        ArbitrationCandidate(id="c2", score=0.5, cost=1.0, kind="l0", payload={}),
        ArbitrationCandidate(id="c3", score=0.8, cost=1.0, kind="l0", payload={}),
    ]
    decision = engine.arbitrate(candidates, policy)
    assert "c2" not in decision.winner_ids
    assert "c1" in decision.winner_ids
    assert "c3" in decision.winner_ids


def test_arbitration_engine_deterministic():
    engine = ArbitrationEngine()
    policy = ArbitrationPolicy(max_winners=2)
    candidates = [
        ArbitrationCandidate(id=f"c{i}", score=float(i) / 10, cost=1.0, kind="x", payload={})
        for i in range(5)
    ]
    d1 = engine.arbitrate(candidates, policy)
    d2 = engine.arbitrate(candidates, policy)
    assert d1.winner_ids == d2.winner_ids
    assert d1.policy_digest == d2.policy_digest
