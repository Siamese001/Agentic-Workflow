"""Unit tests for ``agentic_core.L0_routing.reasoning.r5_reason_calibration``.

Plan: ``.windsurf/plans/routing-decision-process-enhancement-9c7e4d.md`` W5.
"""

from __future__ import annotations

import sqlite3
import time
import uuid

import pytest

from agentic_core.L0_routing.reasoning.r5_reason_calibration import (
    KNOWN_R5_REASONS,
    analyze_r5_reasons,
)
from agentic_core.L6_observability.decision_events_schema import (
    DecisionEventRow,
    ensure_schema,
    insert_decision_event,
)


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)
    return conn


def _insert_r5(
    conn: sqlite3.Connection,
    *,
    reasons: tuple[str, ...],
    outcome_success: bool,
) -> None:
    row = DecisionEventRow(
        decision_id=str(uuid.uuid4()),
        timestamp=time.time(),
        decision_layer="L0_routing",
        app_name="test",
        request_hash="r",
        chosen_route="R5",
        policy_hash="p",
        snapshot_id="s",
        calibration_version="c",
        judge_version="j",
        provenance_digest="d",
        reason_codes=reasons,
        outcome_success=outcome_success,
    )
    insert_decision_event(conn, row)


def test_no_data_returns_empty_report() -> None:
    conn = _conn()
    report = analyze_r5_reasons(conn, min_observations=1)
    assert report.per_reason == {}
    assert report.demoted == set()


def test_well_calibrated_reason_not_demoted() -> None:
    """If a reason fires AND every triggered dispatch DID fail, Brier=0 → not demoted."""
    conn = _conn()
    for _ in range(25):
        _insert_r5(conn, reasons=("low_confidence",), outcome_success=False)
    report = analyze_r5_reasons(conn, min_observations=20, brier_demote_threshold=0.30)
    cal = report.per_reason["low_confidence"]
    assert cal.brier_score == pytest.approx(0.0)
    assert cal.demoted is False
    assert "low_confidence" not in report.demoted


def test_noisy_reason_demoted() -> None:
    """If a reason fires but ~all dispatches succeeded, Brier=1 → demoted."""
    conn = _conn()
    for _ in range(25):
        _insert_r5(conn, reasons=("toxicity_flagged",), outcome_success=True)
    report = analyze_r5_reasons(conn, min_observations=20, brier_demote_threshold=0.30)
    cal = report.per_reason["toxicity_flagged"]
    assert cal.brier_score == pytest.approx(1.0)
    assert cal.demoted is True
    assert "toxicity_flagged" in report.demoted
    assert cal.success_rate_when_triggered == pytest.approx(1.0)


def test_insufficient_data_does_not_demote() -> None:
    conn = _conn()
    for _ in range(5):
        _insert_r5(conn, reasons=("ood_score",), outcome_success=True)
    report = analyze_r5_reasons(conn, min_observations=20)
    assert "ood_score" in report.insufficient_data
    assert report.per_reason["ood_score"].demoted is False
    assert "ood_score" not in report.demoted


def test_unknown_reasons_ignored() -> None:
    """Reasons outside the closed vocabulary are dropped silently."""
    conn = _conn()
    for _ in range(20):
        _insert_r5(conn, reasons=("future_reason_foo",), outcome_success=True)
    report = analyze_r5_reasons(conn, min_observations=10)
    assert "future_reason_foo" not in report.per_reason


def test_multi_reason_dispatch_credits_each() -> None:
    """A row with two reasons increments BOTH reasons' counters once."""
    conn = _conn()
    for _ in range(20):
        _insert_r5(
            conn,
            reasons=("low_confidence", "ood_score"),
            outcome_success=False,
        )
    report = analyze_r5_reasons(conn, min_observations=10)
    assert report.per_reason["low_confidence"].n_observations == 20
    assert report.per_reason["ood_score"].n_observations == 20
    # Both well-calibrated (failure followed each trigger)
    assert not report.per_reason["low_confidence"].demoted
    assert not report.per_reason["ood_score"].demoted


def test_known_r5_reasons_complete() -> None:
    """Sanity — every documented R5 trigger is in the closed vocabulary."""
    expected = {
        "low_confidence",
        "ood_score",
        "circuit_breaker_open",
        "budget_exceeded",
        "clarification_needed",
        "toxicity_flagged",
    }
    assert KNOWN_R5_REASONS == expected


def test_to_dict_serializable() -> None:
    conn = _conn()
    for _ in range(20):
        _insert_r5(conn, reasons=("low_confidence",), outcome_success=False)
    report = analyze_r5_reasons(conn, min_observations=10)
    payload = report.to_dict()
    assert "low_confidence" in payload["per_reason"]
    assert isinstance(payload["demoted"], list)
    assert isinstance(payload["insufficient_data"], list)
